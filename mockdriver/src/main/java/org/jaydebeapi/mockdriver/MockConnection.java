package org.jaydebeapi.mockdriver;

import java.lang.reflect.Field;
import java.sql.Connection;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Types;
import org.mockito.Mockito;

public abstract class MockConnection implements Connection {

    ResultSet mockResultSet;

    public final void mockExceptionOnCommit(String className, String exceptionMessage) throws SQLException {
        Throwable exception = createException(className, exceptionMessage);
        Mockito.doThrow(exception).when(this).commit();
    }

    public final void mockExceptionOnRollback(String className, String exceptionMessage) throws SQLException {
        Throwable exception = createException(className, exceptionMessage);
        Mockito.doThrow(exception).when(this).rollback();
    }

    public final void mockExceptionOnExecute(String className, String exceptionMessage) throws SQLException {
        PreparedStatement mockPreparedStatement = Mockito.mock(PreparedStatement.class);
        Statement mockStatement = Mockito.mock(Statement.class);
        Throwable exception = createException(className, exceptionMessage);
        Mockito.when(mockPreparedStatement.execute()).thenThrow(exception);
        Mockito.when(mockStatement.execute(Mockito.anyString())).thenThrow(exception);
        Mockito.when(this.prepareStatement(Mockito.anyString())).thenReturn(mockPreparedStatement);
        Mockito.when(this.createStatement()).thenReturn(mockStatement);
    }

    public final void mockType(String sqlTypesName) throws SQLException {
        PreparedStatement mockPreparedStatement = Mockito.mock(PreparedStatement.class);
        Statement mockStatement = Mockito.mock(Statement.class);
        Mockito.when(mockPreparedStatement.execute()).thenReturn(true);
        Mockito.when(mockStatement.execute(Mockito.anyString())).thenReturn(true);
        mockResultSet = Mockito.mock(ResultSet.class, "ResultSet(for type " + sqlTypesName + ")");
        Mockito.when(mockPreparedStatement.getResultSet()).thenReturn(mockResultSet);
        Mockito.when(mockStatement.getResultSet()).thenReturn(mockResultSet);
        Mockito.when(mockResultSet.next()).thenReturn(true);
        ResultSetMetaData mockMetaData = Mockito.mock(ResultSetMetaData.class);
        Mockito.when(mockResultSet.getMetaData()).thenReturn(mockMetaData);
        Mockito.when(mockMetaData.getColumnCount()).thenReturn(1);
        int sqlTypeCode = extractTypeCodeForName(sqlTypesName);
        Mockito.when(mockMetaData.getColumnType(1)).thenReturn(sqlTypeCode);
        Mockito.when(this.prepareStatement(Mockito.anyString())).thenReturn(mockPreparedStatement);
        Mockito.when(this.createStatement()).thenReturn(mockStatement);
    }

    public final ResultSet verifyResultSet() {
        return Mockito.verify(mockResultSet);
    }

    private static Throwable createException(String className, String exceptionMessage)  {
        try {
            return (Throwable) Class.forName(className).getConstructor(String.class).newInstance(exceptionMessage);
        } catch (Exception e) {
            throw new RuntimeException("Couldn't initialize class " + className + ".", e);
        }
    }

    private static int extractTypeCodeForName(String sqlTypesName) {
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

}
