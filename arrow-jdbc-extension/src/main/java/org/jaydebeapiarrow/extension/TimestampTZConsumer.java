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

import org.apache.arrow.adapter.jdbc.consumer.BaseConsumer;
import org.apache.arrow.adapter.jdbc.consumer.JdbcConsumer;
import org.apache.arrow.util.Preconditions;
import org.apache.arrow.vector.TimeStampMicroTZVector;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Calendar;


/**
 * Consumer which consume timestamp type values from {@link ResultSet}.
 * Write the data to {@link TimeStampMicroTZVector}.
 * TODO: Add TIMEZONE support
 */
public abstract class TimestampTZConsumer {

    /**
     * Creates a consumer for {@link TimeStampMicroTZVector}.
     */
    public static JdbcConsumer<TimeStampMicroTZVector> createConsumer(
            TimeStampMicroTZVector vector, int index, boolean nullable, Calendar calendar) {
        Preconditions.checkArgument(calendar != null, "Calendar cannot be null");
        if (nullable) {
            return new NullableTimestampConsumer(vector, index, calendar);
        } else {
            return new NonNullableTimestampConsumer(vector, index, calendar);
        }
    }

    /**
     * Nullable consumer for timestamp.
     */
    static class NullableTimestampConsumer extends BaseConsumer<TimeStampMicroTZVector> {
        protected final Calendar calendar;

        /**
         * Instantiate a TimestampConsumer.
         */
        public NullableTimestampConsumer(TimeStampMicroTZVector vector, int index, Calendar calendar) {
            super(vector, index);
            this.calendar = calendar;

        }

        @Override
        public void consume(ResultSet resultSet) throws SQLException {
            long microTimeStamp = TimeUtils.parseTimestampAsMicroSeconds(resultSet, columnIndexInResultSet);
            if (!resultSet.wasNull()) {
                // for fixed width vectors, we have allocated enough memory proactively,
                // so there is no need to call the setSafe method here.
                vector.set(currentIndex, microTimeStamp);
            }
            currentIndex++;
        }
    }

    /**
     * Non-nullable consumer for timestamp.
     */
    static class NonNullableTimestampConsumer extends BaseConsumer<TimeStampMicroTZVector> {

        protected final Calendar calendar;

        /**
         * Instantiate a TimestampConsumer.
         */
        public NonNullableTimestampConsumer(TimeStampMicroTZVector vector, int index, Calendar calendar) {
            super(vector, index);
            this.calendar = calendar;
        }

        @Override
        public void consume(ResultSet resultSet) throws SQLException {
            // for fixed width vectors, we have allocated enough memory proactively,
            // so there is no need to call the setSafe method here.
            long microTimeStamp = TimeUtils.parseTimestampAsMicroSeconds(resultSet, columnIndexInResultSet);
            vector.set(currentIndex, microTimeStamp);
            currentIndex++;
        }
    }
}
