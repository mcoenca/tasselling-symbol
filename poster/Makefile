all: pearson.png cosine.png pearson_sim.png cosine_sim.png k.png factorization.png

%.pdf: %.tex
	pdflatex $^

%.png: %.pdf
	convert -density 2000 $^ $@

.PHONY: clean

clean:
	rm -rf *.log
	rm -rf *.aux
	rm -rf *.pdf
	rm -rf *.gz
	rm -rf *latexmk