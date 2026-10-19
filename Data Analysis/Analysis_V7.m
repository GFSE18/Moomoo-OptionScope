function Analysis_V7()
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
    
    % total_cost = 0;
    % total_revenue = 0;
    % ratios = [];
    % column_names = data.Properties.VariableNames;
    % for n = 1:3:length(column_names)
    %     [tc, tr, ~, ~, ~] = trade_simulation(data.(column_names{n}), data.(column_names{n + 1}), data.(column_names{n + 2}),1201);
    %     total_cost = total_cost + tc;
    %     total_revenue = total_revenue + tr;
    %     ratios=[ratios (tr-tc)/tc];
    % end
    % earning_ratio = (total_revenue - total_cost) / total_cost;
    % disp(total_cost)
    % disp(total_revenue)
    % disp(earning_ratio)
    % disp(ratios)

    
    % total_cost = 0;
    % total_revenue = 0;
    % param_values = 101:100:5001;
    % column_names = data.Properties.VariableNames;
    % ratios = zeros(length(param_values), 1);
    % for i = 1:length(param_values)
    %     last_param = param_values(i);
    %     total_cost = 0;
    %     total_revenue = 0;
    %     for n = 1:3:length(column_names)
    %         [tc, tr, ~, ~, ~] = trade_simulation(data.(column_names{n}), data.(column_names{n + 1}), data.(column_names{n + 2}), last_param);
    %         total_cost = total_cost + tc;
    %         total_revenue = total_revenue + tr;
    %     end
    %     ratios(i) = (total_revenue - total_cost) / total_cost;
    % end
    % figure;
    % plot(param_values, ratios, '-o', 'LineWidth', 1.5, 'MarkerSize', 6);
    % xlabel('Parameter Value (Last Parameter of trade\_simulation)');
    % ylabel('Earning Ratio');
    % title('Earning Ratio vs Last Parameter of trade\_simulation');
    % grid on;

    target_data = data.QQQ241211C528000Bid;
    [total_cost, total_revenue, earning_ratio, buy_index, sell_index, buy_mask, sell_mask] = trade_simulation(data.QQQ241211C528000Last, data.QQQ241211C528000Bid, data.QQQ241211C528000Ask, 801);
    disp(total_cost)
    disp(total_revenue)
    disp(earning_ratio)
    disp(buy_index)
    disp(sell_index)
    subplot(2, 1, 1)
    hold on;
    plot(target_data, '-b', 'DisplayName', 'Target Data');
    plot(median_filter(target_data, 5));
    plot(debounce_filter(target_data,1000))
    % buy_indices = find(buy_mask);
    % sell_indices = find(sell_mask); 
    % plot(buy_indices, target_data(buy_indices), '*r', 'MarkerSize', 8, 'DisplayName', 'Buy Points');
    % plot(sell_indices, target_data(sell_indices), '*y', 'MarkerSize', 8, 'DisplayName', 'Sell Points');
    hold off;
    legend show;
    % title('Target Data with Buy and Sell Points');
    % xlabel('Time');
    % ylabel('Price');
    subplot(2,1,2)
    hold on;
    plot(median_filter(target_data, 5))
    plot(median_filter(target_data, 11))
    hold off;
    legend show;
end

function [total_cost, total_revenue, earning_ratio, buy_index, sell_index, buy_mask, sell_mask] = trade_simulation(price, bid, ask, period)
    total_cost = 0;
    total_revenue = 0;
    is_buy_signal_cur = false;
    is_buy_signal_prev = false;
    has_asset = false;
    buy_index = 0;
    sell_index = 0;
    buy_mask=false(1,length(price));
    sell_mask=false(1,length(price));

    indicator1=median_filter(price,period);
    indicator2=get_MMA(indicator1,100);
    
    for n = period:length(indicator1)

        if indicator1(n) > indicator2(n)
            is_buy_signal_cur = true;
        else
            is_buy_signal_cur = false;
        end

        if is_buy_signal_cur && is_buy_signal_cur ~= is_buy_signal_prev && ~has_asset
            total_cost = total_cost + ask(n);
            buy_index = [buy_index n];
            buy_mask(n)=true;
            has_asset = true;
        end

        if ~is_buy_signal_cur && is_buy_signal_cur ~= is_buy_signal_prev && has_asset
            total_revenue = total_revenue + bid(n);
            sell_index = [sell_index n];
            sell_mask(n)=true;
            has_asset = false;
        end

        if n == length(indicator1) - 60 && has_asset
            total_revenue = total_revenue + bid(n);
            has_asset = false;
            sell_index = [sell_index n];
            sell_mask(n) = true;
        end

        is_buy_signal_prev = is_buy_signal_cur;
    end

    earning_ratio = (total_revenue - total_cost) / total_cost;
end

function out=get_MMA(data,period)
    mma=[];
    for n=1:length(data)
        if n<=period
            temp=sum(data(1:n))/n;
            mma=[mma temp];
        else
            temp=((period-1)*mma(end)+data(n))/period;
            mma=[mma temp];
        end
    end
    out=mma;
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

function filtered_data = debounce_filter(data, threshold)
    % Inputs:
    %   data - Input vector (e.g., time-series data)
    %   threshold - Number of consecutive samples required to confirm a change
    if ~isvector(data)
        error('Input data must be a vector.');
    end

    % Initialize filtered output
    filtered_data = data; % Start with a copy of the original data
    stable_value = data(1); % Start with the first value as stable
    counter = 0; % Counter to check duration of stability

    for i = 2:length(data)

        if data(i) == stable_value
            % If value remains stable, reset counter
            counter = 0;
        else
            % If value changes, increment the counter
            counter = counter + 1;

            % Confirm change if it persists for 'threshold' samples
            if counter >= threshold
                stable_value = data(i); % Accept the change
                counter = 0; % Reset the counter
            end

        end

        filtered_data(i) = stable_value; % Assign the stable value
    end

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
