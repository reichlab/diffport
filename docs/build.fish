#!/usr/bin/env fish
make singlehtml
yes | mv build/singlehtml/* ./
touch .nojekyll
