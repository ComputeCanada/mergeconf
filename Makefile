CHANGELOG	:= CHANGELOG.md
SOURCES		:= mergeconf/*.py
VERSION		:= $(shell git describe --tags | sed -e 's/^v//' -e 's/-/+/' -e 's/-/./g')
PACKAGES	:= dist/mergeconf-$(VERSION)-py3-none-any.whl dist/mergeconf-$(VERSION).tar.gz

all: $(PACKAGES)

.PHONY: release
release:
	@sed -i '' -e 's/\(version =\) .*/\1 '$(VERSION)'/' setup.cfg
	@printf "# Changelog\n\n" > $(CHANGELOG)
	@format='## %(tag) (%(*committerdate:format:%Y-%m-%d)) %(subject)%0a%0a%(body)' ; \
        tags=`git for-each-ref refs/tags \
                 --format='%(objecttype) %(refname:lstrip=2)' \
                | awk '$$1 == "tag" { print $2 }'`; \
        git tag --list --sort=-\*committerdate \
                --format="$$format" $$tags \
	>> $(CHANGELOG)

# fails if version doesn't match specific pattern, so as not to publish
# development version.
.PHONY: checkversion
checkversion:
	@echo "Checking that $(VERSION) is a release version"
	@[[ $(VERSION) =~ ^([0-9]+\.)*[0-9]+$$ ]]
	@echo "Checking that $(VERSION) is in setup.cfg"
	@grep -qw "$(VERSION)" setup.cfg

$(PACKAGES): $(SOURCES)
	@echo Version: $(VERSION)
	@python3 -m build

docs/%.md: mergeconf/%.py misc/pdoc-templates/text.mako
	@pdoc3 --template-dir=misc/pdoc-templates mergeconf.$* > $@

docs: docs/mergeconf.md docs/mergeconfsection.md docs/mergeconfvalue.md docs/exceptions.md

publish-test: $(PACKAGES) checkversion
	@python3 -m twine upload --repository testpypi $(PACKAGES)

publish: $(PACKAGES) checkversion
	@python3 -m twine upload --repository pypi $(PACKAGES)
