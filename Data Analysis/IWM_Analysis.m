function IWM_Analysis()
    file_name = 'IWM241205.csv';
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
    target_data1=data.BidP;
    hold on;
    plot(target_data1);
    plot(movavg(target_data1,"modified",500));
    plot(movavg(target_data1, "simple", 500));
    legend show;
    hold off;
end