use std::fmt::Display;
use std::fs;
use std::os::unix::fs::MetadataExt;
use std::path::PathBuf;

use gray_matter::engine::YAML;
use gray_matter::{self, Matter, Pod};
use relative_path::{PathExt, RelativePathBuf};
use walkdir::{DirEntry, WalkDir};

use crate::errors::Error;

pub struct PostFilter {
    base: Vec<DirEntry>,
    path: PathBuf,
}

impl PostFilter {
    pub fn find(path: &PathBuf) -> Self {
        let walker = WalkDir::new(path).into_iter();
        let filtered = walker.map(Result::unwrap).filter(is_markdown);
        Self {
            base: filtered.collect(),
            path: path.clone(),
        }
    }
    pub fn len(&self) -> usize {
        self.base.len()
    }
    pub fn index(&self, i: usize) -> Option<&DirEntry> {
        self.base.get(i)
    }
    pub fn post(&self, index: usize) -> Option<Post> {
        let path = self.index(index)?.clone().into_path();
        let root = self.path.to_path_buf();
        Some(Post::new(path, root).unwrap())
    }
}

#[derive(Debug)]
pub struct Post {
    path: PathBuf,
    parsed: gray_matter::ParsedEntity,
    rel: RelativePathBuf,
}

fn is_markdown(entry: &walkdir::DirEntry) -> bool {
    entry
        .file_name()
        .to_str()
        .map(|s| s.ends_with("markdown") || s.ends_with("md"))
        .unwrap_or(false)
}

impl Post {
    pub fn new(path: PathBuf, root: PathBuf) -> Result<Self, Error> {
        let relpath = path.parent().unwrap().relative_to(root)?;
        let contents = fs::read_to_string(&path)?;

        let mut matter = Matter::<YAML>::new();
        matter.excerpt_delimiter = Some("<!--more-->".to_string());

        Ok(Self {
            path,
            parsed: matter.parse(&contents),
            rel: relpath,
        })
    }

    pub fn get(&self, key: &String) -> Option<Pod> {
        log::trace!("get({})", key);
        // First we check to see if we have a valid value in our parsed ata
        match &self.parsed.data {
            Some(Pod::Hash(hash)) => hash.get(key).cloned(),
            _ => None,
        }
        // Otherwise, we look for a builtin value
        .or(match key.as_str() {
            // These will match our FrontmatterModel in Django
            // File system fields
            "inode" => self.pod_inode(),
            "path" => self.pod_path(),
            // Full copy of our frontmatter
            "metadata" => self.parsed.data.clone(),
            // Body of our target file
            "content" => self.pod_content(),
            "excerpt" => self.pod_excerpt(),
            // Extra generated fields
            "slug" => self.pod_slug(),
            "dir" => self.pod_dir(),
            "date" => self.pod_date(),
            _ => None,
        })
    }
}

impl Post {
    #[inline]
    fn pod_path(&self) -> Option<Pod> {
        Some(Pod::String(self.path.to_string_lossy().to_string()))
    }
    #[inline]
    fn pod_dir(&self) -> Option<Pod> {
        Some(Pod::String(self.rel.to_string()))
    }
    #[inline]
    fn pod_date(&self) -> Option<Pod> {
        let time = self.path.metadata().ok()?.modified().ok()?;
        let utc = jiff::Timestamp::try_from(time).ok()?;

        Some(Pod::String(format!("{:?}", utc)))
    }
    #[inline]
    fn pod_content(&self) -> Option<Pod> {
        Some(Pod::String(self.parsed.content.clone()))
    }
    #[inline]
    fn pod_excerpt(&self) -> Option<Pod> {
        self.parsed
            .excerpt
            .as_ref()
            .map(|excerpt| Pod::String(excerpt.clone()))
    }
    #[inline]
    fn pod_slug(&self) -> Option<Pod> {
        Some(Pod::String(
            self.path
                .file_stem()
                .unwrap()
                .to_string_lossy()
                .to_string()
                .to_lowercase(),
        ))
    }

    #[inline]
    fn pod_inode(&self) -> Option<Pod> {
        self.path
            .metadata()
            .ok()
            .map(|metadata| Pod::Integer(metadata.ino() as i64))
    }
}

impl Display for Post {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.path.display())
    }
}

impl Display for PostFilter {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.path.display())
    }
}
