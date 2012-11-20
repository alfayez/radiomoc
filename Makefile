prog:
	occbuild --program csp-sdf-tx.occ
	occbuild --program csp-sdf-rx.occ

clean:
	rm csp-sdf-tx
	rm csp-sdf-rx
