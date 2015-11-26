set term pdfcairo lw 2 font "Times New Roman,15"
#set style fill solid 0.4 border
set output "TFdiag_data_tn_fn_point.pdf"
set yrange [210:250]
#set yrange[-2:2]
set ylabel 'RSSI per symbol'
set xlabel 'symbol index'
plot "TFdiag_data.txt" using 1:2 lw 0.3 ls 2 t "tn" with linepoints,\
	'' using 1:3 lw 0.3 ls 1 t "fn" with linepoints

set output