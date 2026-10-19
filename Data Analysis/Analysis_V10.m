function Analysis_V10()
    file_name = '2024-12-26.csv';
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
    call_bid = data.IWM241226C222000Bid;
    call_ask = data.IWM241226C222000Ask;
    call_price = (call_bid+call_ask)/2;
    put_bid = data.IWM241226P223000Bid;
    put_ask = data.IWM241226P223000Ask;
    put_price = (put_bid+put_ask)/2;
    x=1:length(call_price);
    subplot(5,1,1)
    plot(data.IWMLast)
    subplot(5,1,2)
    plot(call_price)
    subplot(5,1,3)
    plot(put_price)
    subplot(5,1,4)
    hold on;
    put_base = 223 - data.IWMLast;
    put_base_mask = put_base<0;
    put_base(put_base_mask)=0;
    put_premium=put_price-put_base;
    plot(put_premium)
    plot(2 * exp(-0.0008 * x))
    subplot(5,1,5)
    hold on;
    composite=call_price+put_price;
    plot(composite-1)
    plot(1.5*exp(-0.0008*x))
end
