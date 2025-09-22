bundle exec jekyll build
cd _site && jekyll serve --verbose | tee -a ../logs/log.txt
