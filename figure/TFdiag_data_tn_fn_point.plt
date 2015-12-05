set term pdfcairo lw 2 font "Times New Roman,15"
#set style fill solid 0.4 border
set output "TFdiag_data_tn_fn_point_0_20.pdf"
set yrange [210:250]
#set yrange[-2:2]
set ylabel 'RSSI per symbol'
set xlabel 'symbol index'
plot "TFdiag_data_0_20.txt" using 1:2 lw 0.1 pt 2 ps 0.6 t "tn" with points,\
	'' using 1:3 lw 0.1 pt 4 ps 0.6 t "fn" with points

set output