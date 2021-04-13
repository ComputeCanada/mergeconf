# Contributing

Thanks for your interest.  To be honest, at this point I expect none and this
file is just for me to remember how to publish a release.

## Publishing a release (maintainers only)

This is to be carried out on the main branch.

*Note* This procedure is imperfect.  Once the CHANGELOG is created it can't be
committed back to the earlier commit; this causes a divergence in the commit
path just before the tag.  The current workaround is to delete the tag after
updating the changelog and recreating it.

1. Create an annotated tag for the release.  This should be descriptive of the
changes since the last release including new features, updates, and bug fixes.
For example:

    First packaged release

    First semi-mature release ready for use by the world.

    Added:
    * Support for specific types (int, float) as well as str and bool.
      Support for boolean values normalized to be consistent with other
      types.

    Updated:
    * Improved error handling.

2. Ready the release: update the version in `setup.cfg` and update the
changelog.  `CHANGELOG.md` is generated automatically from annotations on
tags.

    $ make release

3. Add `CHANGELOG.md` and `setup.cfg` and ensure they are covered under the
previously generated commit.

    $ git add CHANGELOG.md setup.cfg
    $ git commit --amend

4. Push the changes and annotated tags on the main branch to the repository.

    $ git push --follow-tags

5. Publish to PyPi.

    $ make publish
