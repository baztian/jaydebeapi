import sys, traceback
import tempfile
from itertools import islice

import pyarrow as pa
from pyarrow.cffi import ffi as arrow_c


def convert_jdbc_rs_to_arrow_iterator(rs, batch_size=1024):
    import jpype.imports
    from org.jaydebeapiarrow.extension import JDBCUtils
    
    return JDBCUtils.convertResultSetToIterator(rs, batch_size)


def read_rows_from_arrow_iterator(it, nrows=-1):
    root = None
    rows = []

    nrows_remaining = nrows

    try:
        for root in it:
            batch = pa.jvm.record_batch(root).to_pylist()
            _rows = [tuple(r.values()) for r in batch]
            if nrows_remaining > 0:
                _rows = _rows[:min(len(_rows), nrows_remaining)]
                nrows_remaining -= len(_rows)
            else:
                if nrows > 0:
                    break
            rows.extend(_rows)
    
    except Exception as e:
        traceback.print_exc()
        print(f"Error converting iterator to rows: {e}")
        raise e
    
    finally:
        if root is not None:
            root.clear()
    
    if nrows > 0:
        assert nrows >= len(rows), f"Mismatched number rows: {len(rows)} (expected {nrows})"
    return rows


def create_pyarrow_batches_from_list(rows):
    # TODO: add shape checks
    if len(rows) == 0:
        return []
    
    n_cols = len(rows[0])
    column_wise = [[] for _ in range(n_cols)]
    for row in rows:
        for i, col in enumerate(row):
            column_wise[i].append(col)
    
    batch = pa.RecordBatch.from_pydict(
        {"col_{}".format(i): column_wise[i] for i in range(n_cols)}
    )
    return [batch, ]


def add_pyarrow_batches_to_statement(batches, prepared_statement):
    import jpype.imports
    from org.jaydebeapiarrow.extension import JDBCUtils

    if len(batches) == 0:
        return

    print(batches[0].schema)
    reader = pa.RecordBatchReader.from_batches(batches[0].schema, batches)
    c_stream = arrow_c.new("struct ArrowArrayStream*")
    c_stream_ptr = int(arrow_c.cast("uintptr_t", c_stream))
    reader._export_to_c(c_stream_ptr)
    with tempfile.NamedTemporaryFile() as temp:
        JDBCUtils.prepareStatementFromStream(temp.name, c_stream_ptr, prepared_statement)