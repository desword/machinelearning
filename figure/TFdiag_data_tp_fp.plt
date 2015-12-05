set term pdfcairo lw 2 font "Times New Roman,15"
set style data histogram
set style histogram clustered gap 1
set style fill solid 0.4 border
set output "TFdiag_data.pdf"
set key top left
set boxwidth 1
#set xrange [0:90]
set yrange [210:250]
set ylabel 'Per symbol RSSI'
set xlabel 'symbol position'
plot "TFdiag_data.txt" using 2:xtic(10) title "tn" ,\
    '' using 3:xtic(10) title "fn",\
    '' using 4:xtic(10) title "tp",\
    '' using 5:xtic(10) title "fp"
set output

# average error = 37.52%