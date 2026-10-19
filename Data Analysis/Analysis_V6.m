function Analysis_V6()
    file_name = '2024-12-11.csv';
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
    target_data = data.TSLA241213C450000Last;
    bid = data.TSLA241213C450000Bid;
    ask = data.TSLA241213C450000Ask;
    window_size=40:10:500;
    earning_ratios=zeros(length(window_size));
    for i = 1:length(window_size)
        for j = 1:length(window_size)
            indicator2 = movavg(target_data, "linear", window_size(i));
            indicator3 = movavg(target_data, "linear", window_size(j));
            [~, ~, earning_ratio, ~, ~] = trade_simulation_V2(bid, ask, movavg(target_data, "linear", 30), indicator2, indicator3);
            earning_ratios(i, j) = earning_ratio;
        end
    end
    [X, Y] = meshgrid(window_size, window_size);
    figure;
    surf(X, Y, earning_ratios, 'EdgeColor', 'none');
    colorbar;
    xlabel('Window Size 1');
    ylabel('Window Size 2');
    zlabel('Earning Ratio');
    title('Earning Ratio vs. Window Sizes');
end

function [total_cost, total_revenue, earning_ratio, buy_times, sell_times] = trade_simulation_V2(bid, ask, indicator1, indicator2, indicator3)
    total_cost = 0;
    total_revenue = 0;
    is_buy_signal_cur = false;
    is_sell_signal_cur = false;
    is_buy_signal_prev = false;
    is_sell_signal_prev = false;
    has_asset = false;
    buy_times = 0;
    sell_times = 0;

    for n = 1:length(indicator1)
        is_buy_signal_cur = indicator1(n) > indicator2(n);
        is_sell_signal_cur = indicator1(n) < indicator3(n);

        if is_buy_signal_cur && ~is_buy_signal_prev && ~has_asset
            total_cost = total_cost + ask(n);
            buy_times = buy_times + 1;
            has_asset = true;
        end

        if is_sell_signal_cur && ~is_sell_signal_prev && has_asset
            total_revenue = total_revenue + bid(n);
            sell_times = sell_times + 1;
            has_asset = false;
        end

        if n == length(indicator1) - 100 && has_asset
            total_revenue = total_revenue + bid(n);
            has_asset = false;
            sell_times = sell_times + 1;
        end

        is_buy_signal_prev = is_buy_signal_cur;
        is_sell_signal_prev = is_sell_signal_cur;
    end

    earning_ratio = (total_revenue - total_cost) / total_cost;
end