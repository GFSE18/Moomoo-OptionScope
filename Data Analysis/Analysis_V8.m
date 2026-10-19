function Analysis_V8()
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
    target_data = data.SPY241211C607000Bid;
    subplot(2,1,1)
    hold on;
    plot(target_data)
    % plot(get_MMA(target_data,15))
    plot(median_filter(target_data,1201))
    hold off;
    legend show;
    subplot(2, 1, 2)
    hold on;
    plot(target_data)
    filtered_data = median_filter(target_data, 5);
    plot(filtered_data)
    % plot(get_MMA(target_data, 15)*0.25 + median_filter(target_data, 1201)*0.75)
    % plot(get_MMA(target_data, 15) * 0.75 + median_filter(target_data, 1201) * 0.25)
    hold off;
    legend show;
end

function [total_cost, total_revenue, earning_ratio, buy_indices, sell_indices] = trade_simulation_V4(price, bid, ask, gain_threshold, loss_threshold)
    % Calculate moving averages
    ma1 = get_MMA(price, 300);
    ma2 = get_MMA(price, 600);

    % Initialize variables
    total_cost = 0;
    total_revenue = 0;
    buy_indices = []; % Indices where buys occur
    sell_indices = []; % Indices where sells occur
    has_asset = false;
    cost = 0;
    cooldown = false; % Prevent immediate rebuy after a sell

    % Iterate through price data
    for n = 601:length(price)
        % Check if a buy signal occurs
        is_buy_signal = ma1(n) > ma2(n);

        % Buy conditions
        if is_buy_signal && ~has_asset && ~cooldown
            total_cost = total_cost + ask(n);
            cost = ask(n);
            buy_indices = [buy_indices, n]; % Record the buy index
            has_asset = true;
        end

        % Sell conditions
        if has_asset
            % Calculate percentage change
            gain_or_loss = (price(n) - cost) / cost;

            % Check if gain or loss threshold is reached
            if gain_or_loss >= gain_threshold || gain_or_loss <= loss_threshold
                total_revenue = total_revenue + bid(n);
                sell_indices = [sell_indices, n]; % Record the sell index
                has_asset = false;
                cooldown = true; % Activate cooldown after selling
            end

        end

        % Reset cooldown if ma1 drops below ma2
        if ma1(n) <= ma2(n)
            cooldown = false;
        end

    end

    % Calculate earnings ratio
    if total_cost == 0
        earning_ratio = 0;
    else
        earning_ratio = (total_revenue - total_cost) / total_cost;
    end

end

function [total_cost, total_revenue, earning_ratio, buy_index, sell_index] = trade_simulation_V3(price,bid,ask)
    ma1=get_MMA(price,300);
    ma2=get_MMA(price,600);
    macd=ma1-ma2;
    ma_macd=get_MMA(macd,30);
    total_cost = 0;
    total_revenue = 0;
    is_buy_signal_cur = false;
    is_sell_signal_cur = false;
    is_buy_signal_prev = false;
    is_sell_signal_prev = false;
    has_asset = false;
    buy_index=[];
    sell_index=[];
    for n=601:length(price)
        is_buy_signal_cur=macd(n)>0;
        if is_buy_signal_cur && ~is_buy_signal_prev && ~has_asset
            total_cost = total_cost + ask(n);
            buy_index=[buy_index n];
            has_asset = true;
        end
        if has_asset
            is_sell_signal_cur=macd(n)<ma_macd(n);
        end
        if is_sell_signal_cur && ~is_sell_signal_prev && has_asset
            total_revenue = total_revenue + bid(n);
            sell_index=[sell_index n];
            has_asset = false;
            is_sell_signal_cur=false;
        end
        if n == length(price) - 100 && has_asset
            total_revenue = total_revenue + bid(n);
            has_asset = false;
            sell_index = [sell_index n];
        end
        is_buy_signal_prev = is_buy_signal_cur;
        is_sell_signal_prev = is_sell_signal_cur;
    end
    earning_ratio = (total_revenue - total_cost) / total_cost;
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
    filtered_data = [];
    % Apply median filter based on preceding data
    for i = 1:length(data)
        % Define the window range for preceding data only
        start_idx = max(1, i - window_size + 1); % Start from the current point and go back
        end_idx = i; % End at the current point

        % Extract the window and compute the median
        window = data(start_idx:end_idx);
        filtered_data = [filtered_data median(window, 'omitnan')]; % Ignore NaNs if present
    end

end

function out=get_exponential_MA(data,base,period)
    out=[];
    weights=zeros(1,period);
    weights=weights+base;
    for i=1:length(weights)
        weights(i)=weights(i)^i;
    end
    for i=1:length(data)
        if i<period
            temp = sum(data(1:i)) / i;
            out=[out temp];
        else
            temp=0;
            for j=1:period
                temp=temp+data(i-period+j)*weights(j);
            end
            temp=temp/sum(weights);
            out=[out temp];
        end
    end
end