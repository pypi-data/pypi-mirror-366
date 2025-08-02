use crate::PageRef;

#[derive(Debug, Clone)]
pub enum EmptyTableState {
    Start,
    ReadPage { page: PageRef },
}

#[derive(Debug, Clone, Copy)]
pub enum MoveToRightState {
    Start,
    ProcessPage,
}

#[derive(Debug, Clone, Copy)]
pub enum SeekToLastState {
    Start,
    IsEmpty,
}
