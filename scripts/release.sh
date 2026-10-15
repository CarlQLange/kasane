#!/usr/bin/env zsh
# Copies the playable game into the site repo. Assets go into a folder named
# for the release, so the site's day-long image cache never serves stale art.
set -euo pipefail

root=${0:A:h:h}
site=${1:-$HOME/workspace/personal/web/redfloatplane.lol}
dest=$site/public/arcade/kasane/play

[[ -d $site/.git ]] || { print -u2 "No site repo at $site"; exit 1; }

version=$(git -C $root rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M%S)
[[ -z $(git -C $root status --porcelain 2>/dev/null) ]] || version=$version-dirty
assets=assets-$version

rm -rf $dest
mkdir -p $dest
rsync -a --exclude .DS_Store $root/assets/ $dest/$assets/
for file in index.html manifest.json; do
  sed "s#assets/#$assets/#g" $root/$file > $dest/$file
done

print "Released $version to $dest ($(du -sh $dest | cut -f1))"
