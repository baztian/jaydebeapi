package org.jaydebeapi.mockdriver;

import java.lang.reflect.Field;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Types;
import java.util.Calendar;
import org.mockito.Mockito;

public abstract class MockConnection implements Connection {

  ResultSet mockResultSet;

  private static Throwable createException(String className, String exceptionMessage) {
    try {
      return (Throwable) Class.forName(className).getConstructor(String.class)
          .newInstance(exceptionMessage);
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

  public final void mockExceptionOnCommit(String className, String exceptionMessage)
      throws SQLException {
    Throwable exception = createException(className, exceptionMessage);
    Mockito.doThrow(exception).when(this).commit();
  }

  public final void mockExceptionOnRollback(String className, String exceptionMessage)
      throws SQLException {
    Throwable exception = createException(className, exceptionMessage);
    Mockito.doThrow(exception).when(this).rollback();
  }

  public final void mockExceptionOnExecute(String className, String exceptionMessage)
      throws SQLException {
    PreparedStatement mockPreparedStatement = Mockito.mock(PreparedStatement.class);
    Throwable exception = createException(className, exceptionMessage);
    Mockito.when(mockPreparedStatement.execute()).thenThrow(exception);
    Mockito.when(this.prepareStatement(Mockito.anyString())).thenReturn(mockPreparedStatement);
  }

  public final void mockDateResult(int year, int month, int day) throws SQLException {
    PreparedStatement mockPreparedStatement = Mockito.mock(PreparedStatement.class);
    Mockito.when(mockPreparedStatement.execute()).thenReturn(true);
    mockResultSet = Mockito.mock(ResultSet.class, "ResultSet(for date)");
    Mockito.when(mockPreparedStatement.getResultSet()).thenReturn(mockResultSet);
    Mockito.when(mockResultSet.next()).thenReturn(true);
    ResultSetMetaData mockMetaData = Mockito.mock(ResultSetMetaData.class);
    Mockito.when(mockResultSet.getMetaData()).thenReturn(mockMetaData);
    Mockito.when(mockMetaData.getColumnCount()).thenReturn(1);
    Calendar cal = Calendar.getInstance();
    cal.clear();
    cal.set(Calendar.YEAR, year);
    cal.set(Calendar.MONTH, month - 1);
    cal.set(Calendar.DAY_OF_MONTH, day);
    Date ancientDate = new Date(cal.getTime().getTime());
    Mockito.when(mockResultSet.getDate(1)).thenReturn(ancientDate);
    Mockito.when(mockMetaData.getColumnType(1)).thenReturn(Types.DATE);
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

  public final ResultSet verifyResultSet() {
    return Mockito.verify(mockResultSet);
  }
}
