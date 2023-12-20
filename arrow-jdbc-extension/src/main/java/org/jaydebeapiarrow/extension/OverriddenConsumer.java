/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.jaydebeapiarrow.extension;

import java.math.RoundingMode;
import java.util.Calendar;
import java.sql.Types;

import org.apache.arrow.adapter.jdbc.JdbcFieldInfo;
import org.apache.arrow.adapter.jdbc.JdbcToArrowConfig;
import org.apache.arrow.adapter.jdbc.JdbcToArrowUtils;
import org.apache.arrow.adapter.jdbc.consumer.JdbcConsumer;
import org.apache.arrow.adapter.jdbc.consumer.ArrayConsumer;
import org.apache.arrow.adapter.jdbc.consumer.BigIntConsumer;
import org.apache.arrow.adapter.jdbc.consumer.BinaryConsumer;
import org.apache.arrow.adapter.jdbc.consumer.BitConsumer;
import org.apache.arrow.adapter.jdbc.consumer.DecimalConsumer;
import org.apache.arrow.adapter.jdbc.consumer.DoubleConsumer;
import org.apache.arrow.adapter.jdbc.consumer.FloatConsumer;
import org.apache.arrow.adapter.jdbc.consumer.IntConsumer;
import org.apache.arrow.adapter.jdbc.consumer.MapConsumer;
import org.apache.arrow.adapter.jdbc.consumer.NullConsumer;
import org.apache.arrow.adapter.jdbc.consumer.SmallIntConsumer;
import org.apache.arrow.adapter.jdbc.consumer.TinyIntConsumer;
import org.apache.arrow.adapter.jdbc.consumer.VarCharConsumer;

import org.apache.arrow.vector.*;
import org.apache.arrow.vector.types.pojo.ArrowType;
import org.apache.arrow.vector.complex.ListVector;
import org.apache.arrow.vector.complex.MapVector;

import org.apache.arrow.vector.types.TimeUnit;

public class OverriddenConsumer {

    private static final int JDBC_ARRAY_VALUE_COLUMN = 2;
    private Calendar calendar;

    public OverriddenConsumer(Calendar calendar) {
        this.calendar = calendar;
    }

    public ArrowType getJdbcToArrowTypeConverter(final JdbcFieldInfo fieldInfo) {
        switch (fieldInfo.getJdbcType()) {
            case Types.TIMESTAMP:
                final String timezone;
                if (this.calendar != null) {
                    timezone = this.calendar.getTimeZone().getID();
                } else {
                    timezone = null;
                }
                return new ArrowType.Timestamp(TimeUnit.MICROSECOND, timezone);
            default:
                return JdbcToArrowUtils.getArrowTypeFromJdbcType(fieldInfo, this.calendar);
        }
    }

    public static JdbcConsumer getConsumer(ArrowType arrowType, int columnIndex, boolean nullable,
                                    FieldVector vector, JdbcToArrowConfig config) {

        final Calendar calendar = config.getCalendar();

        switch (arrowType.getTypeID()) {
            case Bool:
                return BitConsumer.createConsumer((BitVector) vector, columnIndex, nullable);
            case Int:
                switch (((ArrowType.Int) arrowType).getBitWidth()) {
                    case 8:
                        return TinyIntConsumer.createConsumer((TinyIntVector) vector, columnIndex, nullable);
                    case 16:
                        return SmallIntConsumer.createConsumer((SmallIntVector) vector, columnIndex, nullable);
                    case 32:
                        return IntConsumer.createConsumer((IntVector) vector, columnIndex, nullable);
                    case 64:
                        return BigIntConsumer.createConsumer((BigIntVector) vector, columnIndex, nullable);
                    default:
                        return null;
                }
            case Decimal:
                final RoundingMode bigDecimalRoundingMode = config.getBigDecimalRoundingMode();
                return DecimalConsumer.createConsumer((DecimalVector) vector, columnIndex, nullable, bigDecimalRoundingMode);
            case FloatingPoint:
                switch (((ArrowType.FloatingPoint) arrowType).getPrecision()) {
                    case SINGLE:
                        return FloatConsumer.createConsumer((Float4Vector) vector, columnIndex, nullable);
                    case DOUBLE:
                        return DoubleConsumer.createConsumer((Float8Vector) vector, columnIndex, nullable);
                    default:
                        return null;
                }
            case Utf8:
            case LargeUtf8:
                return VarCharConsumer.createConsumer((VarCharVector) vector, columnIndex, nullable);
            case Binary:
            case LargeBinary:
                return BinaryConsumer.createConsumer((VarBinaryVector) vector, columnIndex, nullable);
            case Date:
                return DateConsumer.createConsumer((DateDayVector) vector, columnIndex, nullable, calendar);
            case Time:
                return TimeConsumer.createConsumer((TimeMilliVector) vector, columnIndex, nullable);
            case Timestamp:
                if (config.getCalendar() == null) {
                    return TimestampConsumer.createConsumer((TimeStampMicroVector) vector, columnIndex, nullable);
                }
                else {
                    return TimestampTZConsumer.createConsumer((TimeStampMicroTZVector) vector, columnIndex, nullable, calendar);
                }
            case List:
                FieldVector childVector = ((ListVector) vector).getDataVector();
                JdbcConsumer delegate = getConsumer(childVector.getField().getType(), JDBC_ARRAY_VALUE_COLUMN,
                        childVector.getField().isNullable(), childVector, config);
                return ArrayConsumer.createConsumer((ListVector) vector, delegate, columnIndex, nullable);
            case Map:
                return MapConsumer.createConsumer((MapVector) vector, columnIndex, nullable);
            case Null:
                return new NullConsumer((NullVector) vector);
            default:
                // no-op, shouldn't get here
                throw new UnsupportedOperationException("No consumer for Arrow type: " + arrowType);
            }
        }
    }
