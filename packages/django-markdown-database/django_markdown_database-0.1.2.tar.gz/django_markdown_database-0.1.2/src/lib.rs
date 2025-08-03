//! Port of C [vtablog](http://www.sqlite.org/cgi/src/finfo?name=ext/misc/vtablog.c)
use std::ffi::c_int;
use std::marker::PhantomData;
use std::ops::Index;
use std::os::raw::c_char;
use std::path::PathBuf;

use gray_matter::Pod;
use json::Value;
use rusqlite::vtab::{
    Context, CreateVTab, Filters, IndexInfo, VTab, VTabConnection, VTabCursor, VTabKind,
    read_only_module,
};
use rusqlite::{Connection, Result, ffi, vtab};

use crate::errors::Error;
use crate::post::{Post, PostFilter};

mod errors;
mod parse;
mod post;

/// Register the "vtablog" module.
pub fn extension_init(conn: Connection) -> Result<bool> {
    let _ = env_logger::try_init().inspect_err(|err| eprintln!("Error configuring logger {err}"));
    let aux: Option<()> = None;
    conn.create_module("markdowndb", read_only_module::<MarkdownDatabase>(), aux)?;
    Ok(false)
}

/// # Safety
///
/// This is used when sqlite loads our extension
#[allow(clippy::not_unsafe_ptr_arg_deref)]
#[unsafe(no_mangle)]
pub unsafe extern "C" fn sqlite3_extension_init(
    db: *mut ffi::sqlite3,
    pz_err_msg: *mut *mut c_char,
    p_api: *mut ffi::sqlite3_api_routines,
) -> c_int {
    unsafe { Connection::extension_init2(db, pz_err_msg, p_api, extension_init) }
}

/// An instance of the vtablog virtual table
#[repr(C)]
struct MarkdownDatabase {
    /// Base class. Must be first
    base: ffi::sqlite3_vtab,
    /// Base path for this 'database'
    path: PathBuf,
    columns: parse::Columns,
}

impl CreateVTab<'_> for MarkdownDatabase {
    const KIND: VTabKind = VTabKind::Default;
}

unsafe impl<'vtab> VTab<'vtab> for MarkdownDatabase {
    type Aux = ();
    type Cursor = MarkdownDatabaseCursor<'vtab>;

    fn connect(
        _db: &mut VTabConnection,
        _aux: Option<&Self::Aux>,
        args: &[&[u8]],
    ) -> Result<(String, Self)> {
        let mut vtab = Self {
            base: ffi::sqlite3_vtab::default(),
            path: PathBuf::new(),
            columns: parse::Columns::new(),
        };

        let mut schema = None;

        let args = &args[3..];
        for c_slice in args {
            let (param, value) = vtab::parameter(c_slice)?;
            match param {
                "schema" => {
                    if schema.is_some() {
                        return Err(Error::DuplicateParam(param.to_string()).into());
                    }

                    vtab.columns = parse::Columns::parse(value)?;
                    schema = Some(value.to_owned())
                }
                "path" => {
                    let path = PathBuf::from(value)
                        .canonicalize()
                        .map_err(|_err| Error::MissingTarget(value.to_string()))?;

                    if !path.exists() {
                        return Err(Error::MissingTarget(value.to_string()).into());
                    }
                    vtab.path = path;
                }
                _ => {
                    return Err(Error::UnknownParam(param.to_string()).into());
                }
            }
        }
        if schema.is_none() {
            return Err(Error::Schema.into());
        }

        Ok((schema.unwrap(), vtab))
    }

    fn best_index(&self, info: &mut IndexInfo) -> Result<()> {
        log::debug!("best_index({}", self.path.display());
        info.set_estimated_cost(500.);
        info.set_estimated_rows(500);
        Ok(())
    }

    fn open(&'vtab mut self) -> Result<Self::Cursor> {
        log::debug!("open({})", self.path.display());
        Self::Cursor::new(self)
    }
}

/// A cursor for the Series virtual table
#[repr(C)]
struct MarkdownDatabaseCursor<'vtab> {
    /// Base class. Must be first
    base: ffi::sqlite3_vtab_cursor,
    /// The rowid
    row_id: usize,
    phantom: PhantomData<&'vtab MarkdownDatabase>,
    walker: post::PostFilter,
    entry: Option<post::Post>,
}

impl MarkdownDatabaseCursor<'_> {
    fn new(table: &mut MarkdownDatabase) -> Result<Self> {
        Ok(Self {
            base: ffi::sqlite3_vtab_cursor::default(),
            // Current cusor position
            row_id: 0,
            phantom: PhantomData,
            walker: PostFilter::find(&table.path),
            entry: None,
        })
    }

    #[allow(dead_code)]
    fn vtab(&self) -> &MarkdownDatabase {
        unsafe { &*(self.base.pVtab as *const MarkdownDatabase) }
    }

    fn handle(&self) -> Result<&Post> {
        match self.entry.as_ref() {
            Some(handle) => Ok(handle),
            None => Err(Error::MissingHandle.into()),
        }
    }
}

unsafe impl VTabCursor for MarkdownDatabaseCursor<'_> {
    /// Begin a search of a virtual table.
    /// (See [SQLite doc](https://sqlite.org/vtab.html#the_xfilter_method))
    fn filter(&mut self, _: c_int, _: Option<&str>, _: &Filters<'_>) -> Result<()> {
        log::debug!("filter({})", self.vtab().path.display());
        self.row_id = 0;
        self.entry = self.walker.post(self.row_id);

        Ok(())
    }

    /// Advance cursor to the next row of a result set initiated by
    /// [`filter`](VTabCursor::filter). (See [SQLite doc](https://sqlite.org/vtab.html#the_xnext_method))
    fn next(&mut self) -> Result<()> {
        if self.row_id == self.walker.len() {
            log::debug!("next(None)");
            return Ok(());
        }
        self.row_id += 1;
        if self.row_id < self.walker.len() {
            self.entry = self.walker.post(self.row_id);
            log::debug!("next(path)");
        }

        Ok(())
    }

    /// Must return `false` if the cursor currently points to a valid row of
    /// data, or `true` otherwise.
    /// (See [SQLite doc](https://sqlite.org/vtab.html#the_xeof_method))
    fn eof(&self) -> bool {
        let eof = self.walker.index(self.row_id).is_none();
        log::debug!("eof({})", self.vtab().path.display());
        eof
    }

    /// Find the value for the `i`-th column of the current row.
    /// `i` is zero-based so the first column is numbered 0.
    /// May return its result back to SQLite using one of the specified `ctx`.
    /// (See [SQLite doc](https://sqlite.org/vtab.html#the_xcolumn_method))
    fn column(&self, ctx: &mut Context, i: c_int) -> Result<()> {
        let name = self.vtab().columns.index(i as usize);
        let value = self.handle()?.get(name);

        match value {
            Some(Pod::Array(array)) => {
                let json_str: Value = Pod::Array(array).deserialize().unwrap();
                ctx.set_result::<String>(&json_str.to_string())
            }
            Some(Pod::Boolean(bool)) => ctx.set_result(&bool),
            Some(Pod::Float(float)) => ctx.set_result(&float),
            Some(Pod::Hash(hash)) => {
                let json_str: Value = Pod::Hash(hash).deserialize().unwrap();
                ctx.set_result::<String>(&json_str.to_string())
            }
            Some(Pod::Integer(integer)) => ctx.set_result(&integer),
            Some(Pod::Null) => Ok(()),
            Some(Pod::String(string)) => ctx.set_result(&string),
            None => Ok(()),
        }
    }

    /// Return the rowid of row that the cursor is currently pointing at.
    /// (See [SQLite doc](https://sqlite.org/vtab.html#the_xrowid_method))
    fn rowid(&self) -> Result<i64> {
        Ok(self.row_id as i64)
    }
}
