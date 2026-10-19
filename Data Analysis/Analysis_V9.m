function Analysis_V9()
    % === Editable parameters ===
    windowSize = 150; % Window size for rolling avg/std
    zeroThreshold = 0.00; % Threshold for rolling average crossover detection
    minSeparation = 100; % Minimum separation between marked points (in indices)
    % ===========================

    file_name = '2024-12-12.csv';
    firstRow = readcell(file_name, 'Range', '1:1');
    opts = detectImportOptions(file_name);
    opts.VariableNames = firstRow;
    numCols = numel(firstRow);
    defaultType = 'double';
    opts.VariableTypes = repmat({defaultType}, 1, numCols);
    timeIdx = strcmp(opts.VariableNames, 'Time');

    if any(timeIdx)
        opts.VariableTypes{timeIdx} = 'char';
    end

    data = readtable(file_name, opts);
    target_data = data.SPYLast;

    % Calculate per-second change (first derivative)
    per_second_change = [NaN; diff(target_data)];

    % Calculate per-second change of per-second change (second derivative)
    second_derivative = [NaN; diff(per_second_change)];

    % Moving standard deviation
    rolling_std_change = movstd(per_second_change, windowSize, 'omitnan');
    rolling_std_second_derivative = movstd(second_derivative, windowSize, 'omitnan');

    % Rolling average of first derivative
    rolling_avg_change = movmean(per_second_change, windowSize, 'omitnan');

    % Detect crossings of the rolling average threshold
    validIdx = ~isnan(rolling_avg_change);
    above = rolling_avg_change(validIdx) > zeroThreshold;
    below = rolling_avg_change(validIdx) < zeroThreshold;
    cross = diff(above - below);
    avgCrossRelIdx = find(cross ~= 0) + 1;
    fullValidIdx = find(validIdx);
    avgCrossIdx = fullValidIdx(avgCrossRelIdx);

    % Apply separation filter
    filteredCrossIdx = [];
    lastIdx = -inf;

    for i = 1:length(avgCrossIdx)

        if avgCrossIdx(i) - lastIdx >= minSeparation
            filteredCrossIdx(end + 1) = avgCrossIdx(i); %#ok<AGROW>
            lastIdx = avgCrossIdx(i);
        end

    end

    % Plotting
    figure;

    subplot(3, 1, 1);
    plot(target_data);
    hold on;
    plot(filteredCrossIdx, target_data(filteredCrossIdx), 'ro', 'MarkerSize', 8, 'DisplayName', 'Filtered Crossings');
    hold off;
    title('SPY Last Price');
    ylabel('Price');
    legend('show');

    subplot(3, 1, 2);
    plot(rolling_avg_change);
    hold on;
    yline(zeroThreshold, '--k', 'LineWidth', 1.2, 'DisplayName', 'Avg Threshold');
    plot(filteredCrossIdx, rolling_avg_change(filteredCrossIdx), 'ro', 'MarkerSize', 4);
    hold off;
    title(sprintf('Rolling Avg of Per-Second Change (%d-Index Window)', windowSize));
    xlabel('Time Index');
    ylabel('Avg Change');
    legend('show');

    subplot(3, 1, 3);
    plot(rolling_std_change, 'b', 'DisplayName', 'MovStd of Per-Second Change');
    hold on;
    plot(rolling_std_second_derivative, 'r', 'DisplayName', 'MovStd of Second Derivative');
    plot(filteredCrossIdx, rolling_std_change(filteredCrossIdx), 'bo', 'MarkerSize', 4);
    plot(filteredCrossIdx, rolling_std_second_derivative(filteredCrossIdx), 'ro', 'MarkerSize', 4);
    hold off;
    title(sprintf('Rolling Std Dev (%d-Index Window)', windowSize));
    xlabel('Time Index');
    ylabel('Std Dev');
    legend('show');
end
