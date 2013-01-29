prog:
	occbuild --program csp-sdf-tx.occ
	occbuild --program csp-sdf-rx.occ
	occbuild --program csp-sdf-sim.occ

clean:
	rm csp-sdf-tx
	rm csp-sdf-rx
	rm csp-sdf-sim
