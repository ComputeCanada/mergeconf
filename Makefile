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

$(PACKAGES): $(SOURCES)
	@echo Version: $(VERSION)
	@sed -i '' -e 's/\(version =\) .*/\1 '$(VERSION)'/' setup.cfg
	@python3 -m build

upload-test: $(PACKAGES) checkversion
	@python3 -m twine upload --repository testpypi $(PACKAGES)

upload: $(PACKAGES) checkversion
	@python3 -m twine upload --repository pypi $(PACKAGES)
