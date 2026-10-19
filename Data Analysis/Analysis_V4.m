function Analysis_V4()
    % File name
    file_name = 'IWM241205.csv';

    % Read the first row for variable names
    firstRow = readcell(file_name, 'Range', '1:1');

    % Detect import options
    opts = detectImportOptions(file_name);
    opts.VariableNames = firstRow;

    % Configure variable types
    numCols = numel(firstRow);
    defaultType = 'double';
    opts.VariableTypes = repmat({defaultType}, 1, numCols);

    % Adjust type for the 'Time' column, if present
    timeIdx = strcmp(opts.VariableNames, 'Time');

    if any(timeIdx)
        opts.VariableTypes{timeIdx} = 'char';
    end

    % Read the table
    data = readtable(file_name, opts);
    target_data = data.BidC;

    % Define window sizes
    window_sizes = 100:100:5000;
    n = length(window_sizes);
    gaps_store = cell(n, n); % Preallocate a cell array to store gaps

    % Compute gaps for each combination
    for i = 1:n

        for j = i:n
            ma1 = movavg(target_data, "linear", window_sizes(i));
            ma2 = movavg(target_data, "linear", window_sizes(j));
            gaps = get_MA_crossing_gaps(ma1, ma2);
            gaps_store{i, j} = gaps; % Store gaps for this combination
        end

    end

    % Plot kernel density diagrams
    figure;
    hold on;
    colors = lines(n * n); % Generate unique colors for lines
    legend_entries = {}; % To store legend text

    count = 1; % Counter for color indexing
    h_lines = gobjects(n * n, 1); % Preallocate handle array for lines

    for i = 1:n

        for j = i:n

            if ~isempty(gaps_store{i, j})
                % Compute kernel density
                [f, xi] = ksdensity(gaps_store{i, j});
                % Plot density with a unique color
                h_lines(count) = plot(xi, f, 'LineWidth', 1.5, 'Color', colors(count, :));
                % Add entry to legend
                legend_entries{end + 1} = sprintf('MA(%d, %d)', window_sizes(i), window_sizes(j));
                count = count + 1;
            end

        end

    end

    % Customize plot
    xlabel('Gap Length');
    ylabel('Density');
    title('Kernel Density of Gaps for MA Combinations');
    legend(legend_entries, 'Location', 'Best', 'Interpreter', 'none'); % Add legend
    hold off;

    % Enable data cursor mode for interactive legend display
    dcm_obj = datacursormode(gcf);
    set(dcm_obj, 'Enable', 'on', 'UpdateFcn', @myDataCursorFunction);

    % Custom data cursor function to display combination information
    function txt = myDataCursorFunction(~, event_obj)
        % Get the index of the selected data point
        idx = event_obj.DataIndex;
        % Return the corresponding legend entry for the selected line
        txt = legend_entries{idx};
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
