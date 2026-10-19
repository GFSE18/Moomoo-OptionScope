function QQQCP_Analysis()
    % Load and prepare data
    file_name = 'QQQ241204CP520000.csv';
    opts = detectImportOptions(file_name);
    opts.VariableNames = {'Time', 'LastPriceC', 'BidC', 'AskC', 'LastPriceP', 'BidP', 'AskP'};
    opts.VariableTypes = {'datetime', 'double', 'double', 'double', 'double', 'double', 'double'};
    opts = setvaropts(opts, 'Time', 'InputFormat', 'MM/dd/yyyy HH:mm');
    data = readtable(file_name, opts);
    plot(data.BidP)
end