package org.jaydebeapi.mockdriver;

import java.lang.reflect.Field;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Types;
import org.mockito.Mockito;

public abstract class MockConnection implements Connection {

    ResultSet mockResultSet;

    public final void mockExceptionOnExecute(String exceptionMessage) throws SQLException {
        PreparedStatement mockPreparedStatement = Mockito.mock(PreparedStatement.class);
        Mockito.when(mockPreparedStatement.execute()).thenThrow(new SQLException(exceptionMessage));
        Mockito.when(this.prepareStatement(Mockito.anyString())).thenReturn(mockPreparedStatement);
    }

    public final void mockType(String sqlTypesName) throws SQLException {
        PreparedStatement mockPreparedStatement = Mockito.mock(PreparedStatement.class);
        Mockito.when(mockPreparedStatement.execute()).thenReturn(true);
        mockResultSet = Mockito.mock(ResultSet.class, "ResultSet(for type " + sqlTypesName + ")");
        Mockito.when(mockPreparedStatement.getResultSet()).thenReturn(mockResultSet);
        Mockito.when(mockResultSet.next()).thenReturn(true);
        ResultSetMetaData mockMetaData = Mockito.mock(ResultSetMetaData.class);
        Mockito.when(mockResultSet.getMetaData()).thenReturn(mockMetaData);
        Mockito.when(mockMetaData.getColumnCount()).thenReturn(1);
        int sqlTypeCode = extractTypeCodeForName(sqlTypesName);
        Mockito.when(mockMetaData.getColumnType(1)).thenReturn(sqlTypeCode);
        Mockito.when(this.prepareStatement(Mockito.anyString())).thenReturn(mockPreparedStatement);
    }

    private int extractTypeCodeForName(String sqlTypesName) {
        try {
            Field field = Types.class.getField(sqlTypesName);
            return field.getInt(null);
        } catch (NoSuchFieldException e) {
            throw new IllegalArgumentException("Type " + sqlTypesName + " not found in Types class.", e);
        } catch (SecurityException e) {
            throw new RuntimeException(e);
        } catch (IllegalArgumentException e) {
            throw new RuntimeException(e);
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        }
    }

    public final ResultSet verifyResultSet() {
        return Mockito.verify(mockResultSet);
    }

}
