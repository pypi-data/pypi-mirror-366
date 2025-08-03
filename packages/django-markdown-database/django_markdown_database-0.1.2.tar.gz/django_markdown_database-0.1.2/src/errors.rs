#[derive(Debug)]
pub enum Error {
    Schema,
    DuplicateParam(String),
    MissingTarget(String),
    UnknownParam(String),
    MissingHandle,
    SchemaParse,
    SchemaNotCreate,
    SchemaMissingColumns,
    FileError(std::io::Error),
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Schema => write!(f, "Error with schema"),
            Self::DuplicateParam(param) => write!(f, "more than one '{}' parameter", param),
            Self::MissingTarget(path) => write!(f, "target directory '{}' missing", path),
            Self::UnknownParam(param) => write!(f, "more than one '{}' parameter", param),
            Self::MissingHandle => write!(f, "Missing handle to file"),
            Self::SchemaParse => write!(f, "Error parsing schema"),
            Self::SchemaNotCreate => write!(f, "Not CREATE statement"),
            Self::SchemaMissingColumns => write!(f, "Missing columns"),
            Self::FileError(err) => write!(f, "{err}"),
        }
    }
}

impl From<Error> for rusqlite::Error {
    fn from(val: Error) -> Self {
        rusqlite::Error::ModuleError(val.to_string())
    }
}

impl From<relative_path::RelativeToError> for Error {
    fn from(val: relative_path::RelativeToError) -> Self {
        Self::MissingTarget(val.to_string())
    }
}

impl From<std::io::Error> for Error {
    fn from(val: std::io::Error) -> Self {
        Self::FileError(val)
    }
}

impl std::error::Error for Error {}
