set term pdfcairo lw 2 font "Times New Roman,15"
#set style fill solid 0.4 border
set output "TFdiag_data_tp_fp_point.pdf"
set yrange [210:250]
#set yrange[-2:2]
set ylabel 'RSSI per symbol'
set xlabel 'symbol index'
plot "TFdiag_data.txt" using 1:4 lw 0.1 pt 2 ps 0.6 t "tp" with points,\
	'' using 1:5 lw 0.1 pt 4 ps 0.6 t "fp" with points

set output