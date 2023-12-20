package org.jaydebeapiarrow.extension;

import java.sql.*;
import java.util.*;
import java.util.logging.Logger;

import com.jakewharton.fliptables.FlipTable;
import org.apache.arrow.adapter.jdbc.JdbcFieldInfo;

public class ExplicitTypeMapper {

    private static final Logger logger = Logger.getLogger(ExplicitTypeMapper.class.getName());
    private int defaultDecimalPrecision = 38;
    private int defaultDecimalScale = 17;

    public ExplicitTypeMapper() {
    }

    public ExplicitTypeMapper(int defaultDecimalPrecision, int defaultDecimalScale) {
        this.defaultDecimalScale = defaultDecimalScale;
        this.defaultDecimalPrecision = defaultDecimalPrecision;
    }


    static Map<Integer, List<Integer>> parseMetaData(ResultSet resultSet) throws SQLException {
        ResultSetMetaData metaData = resultSet.getMetaData();
        List<String[]> tabularMetaData = new ArrayList<>();
        Map<Integer, List<Integer>> parsedMetaData = new HashMap<>();

        String[] headers = {
                "columnName",
                "columnTypeName",
                "inferredColumnTypeName",
                "columnNullable",
        };

        for (int columnIndex = 1; columnIndex <= metaData.getColumnCount(); columnIndex++) {
            int columnType = metaData.getColumnType(columnIndex);
            String columnName = metaData.getColumnName(columnIndex);
            String columnTypeName = metaData.getColumnTypeName(columnIndex);
            String inferredColumnTypeName = JDBCType.valueOf(columnType).getName();
            int columnNullable = metaData.isNullable(columnIndex);

            String[] columnMetaData = {
                    columnName,
                    columnTypeName,
                    inferredColumnTypeName,
                    ((Integer) columnNullable).toString(),
            };
            tabularMetaData.add(columnMetaData);

            List<Integer> columnsWithSameType = parsedMetaData.getOrDefault(columnType, new ArrayList<Integer>());
            columnsWithSameType.add(columnIndex);
            parsedMetaData.put(columnType, columnsWithSameType);
        }

        String[][] columnMetaDataArray = new String[tabularMetaData.size()][];
        logger.info("\n" + FlipTable.of(
                headers,
                tabularMetaData.toArray(columnMetaDataArray)
        ));

        return parsedMetaData;
    }

    private JdbcFieldInfo createDefaultDecimalFieldInfo(int precision, int scale) {
        if (precision < 1) {
            return new JdbcFieldInfo(
                    Types.DECIMAL,
                    defaultDecimalPrecision,
                    defaultDecimalScale
                    );
        }
        else {
            return new JdbcFieldInfo(
                    Types.DECIMAL,
                    precision,
                    scale
            );
        }
    }

    public Map<Integer, JdbcFieldInfo> createExplicitTypeMapping(ResultSet resultSet) throws SQLException {
        Map<Integer, List<Integer>> parsedMetaData = parseMetaData(resultSet);

        Map<Integer, JdbcFieldInfo> explicitMapping = new HashMap<>();

        /* correctly marked as Decimal */
        List<Integer> decimalColumnIndices = parsedMetaData.getOrDefault(Types.DECIMAL, new ArrayList<>());
        decimalColumnIndices.addAll(parsedMetaData.getOrDefault(Types.NUMERIC, new ArrayList<>()));

        /* inferred as Decimal */
        for (int columnIndex: parsedMetaData.getOrDefault(Types.INTEGER, new ArrayList<>())) {
            if (resultSet.getMetaData().getColumnName(columnIndex).contains("DECIMAL")) {
                logger.info(String.format("Inferred column %1s (%2s) as a Decimal", columnIndex, resultSet.getMetaData().getColumnName(columnIndex)));
                decimalColumnIndices.add(columnIndex);
            }
        }

        for (int columnIndex: decimalColumnIndices) {
            int precision = resultSet.getMetaData().getPrecision(columnIndex);
            int scale = resultSet.getMetaData().getScale(columnIndex);
            String columnName = resultSet.getMetaData().getColumnName(columnIndex);
            JdbcFieldInfo decimalFieldInfo = createDefaultDecimalFieldInfo(precision, scale);
            explicitMapping.put(columnIndex, decimalFieldInfo);
            logger.info(String.format("Detected column %1s (%2s) as a Decimal: (%3s, %4s) -> (%5s, %6s)",
                    columnIndex, columnName, precision, scale,
                    decimalFieldInfo.getPrecision(), decimalFieldInfo.getScale()
                    )
            );
        }

        return explicitMapping;
    }

}
