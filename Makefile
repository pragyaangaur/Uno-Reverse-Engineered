CC ?= cc
CFLAGS ?= -O3 -Wall -Wextra

all: engine/uno engine/shortest

engine/uno: engine/uno.c
	$(CC) $(CFLAGS) -o $@ $< -lm

engine/shortest: engine/shortest.c
	$(CC) $(CFLAGS) -o $@ $<

test: all
	cd engine && python3 check_shortest.py
	python3 tests/test_claims.py

figures:
	python3 analysis/figures.py

clean:
	rm -f engine/uno engine/shortest

.PHONY: all test figures clean
