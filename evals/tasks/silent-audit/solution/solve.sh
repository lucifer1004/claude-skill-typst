#!/bin/bash
set -euo pipefail
cat > /app/main.typ <<'EOF'
#set page(paper: "a4", margin: 2.5cm)
#set math.equation(numbering: "(1)")

= On the Alpha-C Estimator for Queueing Networks

== Introduction

We study estimators indexed by a cost parameter. Let $alpha_c (N)$ denote the
estimator at cost $c$ with $N$ samples. Empirically, the estimator achieves a
50% reduction in variance relative to the baseline.

== Main Result

The normalizing constant satisfies

$ frac(cal(Z)(tilde(S)), cal(Z)(0)) = integral_0^infinity e^(-x) dif x $

and the confidence interval for the ratio is $ 1.60 "–" 1.61 $.

== Discussion

The inverse CDF $ Phi^(-1)(x) $ is well-defined on the open interval.
EOF
typst compile /app/main.typ /app/main.pdf
