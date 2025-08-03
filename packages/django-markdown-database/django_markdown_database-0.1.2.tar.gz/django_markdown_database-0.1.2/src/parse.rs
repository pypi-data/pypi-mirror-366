use std::ops::Index;

use rusqlite::Result;
use rusqlite::fallible_iterator::FallibleIterator;
use rusqlite::vtab::dequote;
use sqlite3_parser::ast::{Cmd, CreateTableBody, Stmt};
use sqlite3_parser::lexer::sql::Parser;

use crate::errors::Error;

#[derive(Debug, Clone)]
pub struct Columns(Vec<String>);

impl Columns {
    pub fn new() -> Self {
        Self(Vec::new())
    }

    /// Push a new column name
    /// We need to ensure that our column name is properly
    /// dequoted so we handle that here.
    fn push(&mut self, value: String) {
        self.0.push(dequote(value.as_str()).to_string())
    }
}

impl Index<usize> for Columns {
    type Output = String;

    fn index(&self, index: usize) -> &Self::Output {
        self.0.index(index)
    }
}

impl Columns {
    /// Given a schema declration, return a mapping of columns
    pub fn parse(schema: &str) -> Result<Self> {
        let mut columns = Self::new();
        log::debug!("Parsing statement: {}", schema);
        let mut parser = Parser::new(schema.as_bytes());

        let ast = match parser.next() {
            Ok(Some(ast)) => ast,
            _ => return Err(Error::SchemaParse.into()),
        };

        let create_table = match ast {
            Cmd::Stmt(Stmt::CreateTable {
                temporary: _,
                if_not_exists: _,
                tbl_name: _,
                body,
            }) => body,
            _ => return Err(Error::SchemaNotCreate.into()),
        };

        let column_map = match create_table {
            CreateTableBody::ColumnsAndConstraints {
                columns,
                constraints: _,
                flags: _,
            } => columns,
            _ => return Err(Error::SchemaMissingColumns.into()),
        };
        for col in column_map.iter() {
            columns.push(col.1.col_name.to_string());
        }

        Ok(columns)
    }
}
