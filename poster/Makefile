all: pearson.png cosine.png pearson_sim.png cosine_sim.png k.png

%.pdf: %.tex
	pdflatex $^

%.png: %.pdf
	convert -density 2000 $^ $@
