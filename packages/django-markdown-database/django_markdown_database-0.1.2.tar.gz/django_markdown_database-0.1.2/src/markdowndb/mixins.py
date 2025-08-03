from django.db import models


class FrontmatterModel(models.Model):
    # Fields related to the file system.
    inode = models.PositiveSmallIntegerField(primary_key=True, editable=False)
    path = models.FilePathField(unique=True, editable=False)

    # Full copy of our frontmatter metadata
    metadata = models.JSONField()

    # Body of our target file.
    # Content is the full file while exceprt is everything
    # after a <!--more--> tag
    content = models.TextField()
    excerpt = models.TextField(blank=True)

    # Extra generated fields
    slug = models.SlugField()

    class Meta:
        abstract = True
