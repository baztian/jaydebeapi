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
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Calendar;

import org.apache.arrow.c.ArrowArrayStream;
import org.apache.arrow.c.Data;
import org.apache.arrow.memory.BufferAllocator;
import org.apache.arrow.vector.ipc.ArrowReader;
import org.apache.arrow.adapter.jdbc.ArrowVectorIterator;
import org.apache.arrow.adapter.jdbc.JdbcParameterBinder;
import org.apache.arrow.adapter.jdbc.JdbcToArrow;
import org.apache.arrow.vector.VectorSchemaRoot;
import org.apache.arrow.adapter.jdbc.JdbcToArrowConfig;
import org.apache.arrow.adapter.jdbc.JdbcToArrowConfigBuilder;


public class JDBCUtils {
    
    public JDBCUtils() {}

    public static void prepareStatementFromStream(String path, long cStreamPointer, PreparedStatement statement) throws Exception {
        try (final ArrowArrayStream stream = ArrowArrayStream.wrap(cStreamPointer)) {
            BufferAllocator allocator = AllocatorSingleton.getChildAllocator();
            final ArrowReader input = Data.importArrayStream(allocator, stream);
            VectorSchemaRoot root = input.getVectorSchemaRoot();
            final JdbcParameterBinder binder = 
                JdbcParameterBinder
                .builder(statement, root)
                .bindAll()
                .build();
            while (input.loadNextBatch()) {
                while (binder.next()) {
                    statement.addBatch();
                }
                binder.reset();
            }
        }
    }

    public static ArrowVectorIterator convertResultSetToIterator(ResultSet resultSet, int batchSize) throws Exception {
        try (BufferAllocator allocator = AllocatorSingleton.getChildAllocator()) {
            Calendar calendar = null;
            OverriddenConsumer overriden_consumer = new OverriddenConsumer(calendar);
            JdbcToArrowConfig arrow_jdbc_config = (
                new JdbcToArrowConfigBuilder()
                .setAllocator(allocator)
                .setCalendar(calendar)
                .setTargetBatchSize(batchSize)
                .setBigDecimalRoundingMode(RoundingMode.UNNECESSARY)
                .setExplicitTypesByColumnIndex(new ExplicitTypeMapper().createExplicitTypeMapping(resultSet))
                .setIncludeMetadata(true)
                .setJdbcToArrowTypeConverter((jdbcFieldInfo) -> overriden_consumer.getJdbcToArrowTypeConverter(jdbcFieldInfo))
                .setJdbcConsumerGetter(OverriddenConsumer::getConsumer)
                .build()
            );
            ArrowVectorIterator iterator = JdbcToArrow.sqlToArrowVectorIterator(resultSet, arrow_jdbc_config);
            return iterator;
        }
    }

}



