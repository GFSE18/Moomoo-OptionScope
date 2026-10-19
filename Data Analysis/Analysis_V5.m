function Analysis_V5()
    file_name = '2024-12-11 - Copy.csv';
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
    target_data = data.SPY241211C607000Last;
    subplot(3,1,1)
    hold on;
    plot(target_data)
    plot(movavg(target_data,"simple",60))
    hold off;
    legend show;
    subplot(3,1,2)
    hold on;
    plot(target_data)
    [upper,lower,middle]=bollinger_bands(target_data,300);
    plot(upper)
    plot(lower)
    plot(middle)
    hold off;
    legend show;
    subplot(3,1,3)
    hold on;
    rsi = calculate_RSI(target_data, 600);
    plot(rsi)
    plot(zeros(1, length(target_data)) + 45)
    plot(zeros(1,length(target_data))+50)
    plot(zeros(1, length(target_data)) + 55)
    hold off;
    legend show;
end

function rsi = calculate_RSI(prices, period)
    % Function to calculate Relative Strength Index (RSI)
    % Inputs:
    % - prices: A vector of price data
    % - period: The lookback period for RSI calculation
    % Outputs:
    % - rsi: A vector containing the RSI values

    % Ensure there are enough prices for the given period
    if length(prices) < period
        error('Not enough price data for the given period.');
    end

    % Calculate price changes
    deltas = diff(prices);

    % Initialize gains and losses
    gains = max(deltas, 0); % Positive changes (gains)
    losses = -min(deltas, 0); % Negative changes (losses)

    % Initialize the RSI vector
    rsi = nan(size(prices));

    % Calculate the initial average gain and loss
    avg_gain = mean(gains(1:period));
    avg_loss = mean(losses(1:period));

    % Calculate RSI for the first period
    rs = avg_gain / avg_loss;
    rsi(period) = 100 - (100 / (1 + rs));

    % Calculate RSI for the remaining periods using a rolling average
    for i = period + 1:length(prices)
        avg_gain = ((avg_gain * (period - 1)) + gains(i - 1)) / period;
        avg_loss = ((avg_loss * (period - 1)) + losses(i - 1)) / period;
        rs = avg_gain / avg_loss;
        rsi(i) = 100 - (100 / (1 + rs));
    end

end

function [upper_band, lower_band, middle_band] = bollinger_bands(data, period)
    % Calculates the Bollinger Bands for the given data and period length.
    % Arguments:
    % - data: Input data vector (numeric).
    % - period: The period length for the moving average and standard deviation.
    % Returns:
    % - upper_band: The upper Bollinger Band.
    % - lower_band: The lower Bollinger Band.
    % - middle_band: The moving average (middle band).

    % Validate inputs
    if period <= 0
        error('Period must be a positive integer.');
    end

    if ~isvector(data)
        error('Data must be a vector.');
    end

    % Ensure data is a column vector
    data = data(:);

    % Initialize bands
    n = length(data);
    middle_band = nan(n, 1); % Moving average
    upper_band = nan(n, 1); % Upper band
    lower_band = nan(n, 1); % Lower band
    % Compute bands
    for i = period:n
        window = data(i - period + 1:i);
        middle_band(i)=mean(window);
        std_dev = std(window); % Standard deviation
        upper_band(i) = middle_band(i) + 2 * std_dev; % Upper band
        lower_band(i) = middle_band(i) - 2 * std_dev; % Lower band
    end

end

function out = get_MMA(data, period)
    mma = [];

    for n = 1:length(data)

        if n <= period
            temp = sum(data(1:n)) / n;
            mma = [mma temp];
        else
            temp = ((period - 1) * mma(end) + data(n)) / period;
            mma = [mma temp];
        end

    end

    out = mma;
end

function filtered_data = median_filter(data, window_size)

    if mod(window_size, 2) == 0 || window_size <= 0
        error('Window size must be a positive odd integer.');
    end

    if ~isvector(data)
        error('Input data must be a vector.');
    end

    % Initialize the filtered data
    filtered_data = nan(size(data));

    % Apply median filter based on preceding data
    for i = 1:length(data)
        % Define the window range for preceding data only
        start_idx = max(1, i - window_size + 1); % Start from the current point and go back
        end_idx = i; % End at the current point

        % Extract the window and compute the median
        window = data(start_idx:end_idx);
        filtered_data(i) = median(window, 'omitnan'); % Ignore NaNs if present
    end

end

function out = get_MA_crossing_gaps(ma1, ma2)
    out = [];
    stamp = NaN;
    is_ma1_over_ma2 = ma1(1) > ma2(1);

    for n = 2:length(ma1)

        if (ma1(n) > ma2(n)) ~= is_ma1_over_ma2

            if ~isnan(stamp)
                gap = n - stamp;
                out = [out, gap];
            end

            stamp = n;
            is_ma1_over_ma2 = ~is_ma1_over_ma2;
        end

    end

end