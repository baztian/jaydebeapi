package org.jaydebeapiarrow.extension;

import org.apache.arrow.adapter.jdbc.JdbcToArrowUtils;

import java.sql.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.logging.Logger;

public class TimeUtils {

    private static final Logger logger = Logger.getLogger(ExplicitTypeMapper.class.getName());

    public static long parseDateAsMilliSeconds(ResultSet resultSet, int columnIndexInResultSet) throws SQLException {
        long millis = 0;
        try {
            LocalDate date = resultSet.getObject(columnIndexInResultSet, LocalDate.class);
            if (! resultSet.wasNull()) {
                millis = date.atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli();
            }
        }
        catch (SQLException e) {
            logger.warning(String.format("Can not consume date using getObject (possibly due to lack of support for java.time): %1s", e.getMessage()));
            if (! resultSet.wasNull()) {
                Date date = resultSet.getDate(columnIndexInResultSet, JdbcToArrowUtils.getUtcCalendar());
                millis = date.getTime();
            }
        }
        return millis;
    }

    public static int parseTimeAsMilliSeconds(ResultSet resultSet, int columnIndexInResultSet) throws SQLException {
        int millis = 0;
        try {
            LocalTime time = resultSet.getObject(columnIndexInResultSet, LocalTime.class);
            if (! resultSet.wasNull()) {
                millis = time.toSecondOfDay() * 1000;
            }
        }
        catch (SQLException e) {
            logger.warning(String.format("Can not consume time using getObject (possibly due to lack of support for java.time): %1s", e.getMessage()));
            if (! resultSet.wasNull()) {
                Time time = resultSet.getTime(columnIndexInResultSet, JdbcToArrowUtils.getUtcCalendar());
                millis = (int) time.getTime(); /* since date components set to the "zero epoch" by driver */
            }
        }
        return millis;
    }

    public static long parseTimestampAsMicroSeconds(ResultSet resultSet, int columnIndexInResultSet) throws SQLException {
        long micros = 0;
        try {
            LocalDateTime timestamp = resultSet.getObject(columnIndexInResultSet, LocalDateTime.class);
            if (! resultSet.wasNull()) {
                int fractionalMicroSeconds = timestamp.getNano() / 1000;
                long integralMicroSeconds = timestamp.toEpochSecond(ZoneOffset.UTC) * 1_000_000L;
                micros = integralMicroSeconds + fractionalMicroSeconds;
            }
        }
        catch (SQLException e) {
            logger.warning(String.format("Can not consume timestamp using getObject (possibly due to lack of support for java.time): %1s", e.getMessage()));
            if (! resultSet.wasNull()) {
                Timestamp time = resultSet.getTimestamp(columnIndexInResultSet, JdbcToArrowUtils.getUtcCalendar());
                int fractionalMicroSeconds = time.getNanos() / 1000;
                long integralMicroSeconds = time.getTime() / 1000 * 1_000_000L;
                micros = integralMicroSeconds + fractionalMicroSeconds;
            }
        }
        return micros;
    }
}