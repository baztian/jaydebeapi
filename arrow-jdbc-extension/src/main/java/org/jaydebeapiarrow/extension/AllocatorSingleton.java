package org.jaydebeapiarrow.extension;

import java.util.concurrent.atomic.AtomicInteger;

import org.apache.arrow.memory.BufferAllocator;
import org.apache.arrow.memory.RootAllocator;

public enum AllocatorSingleton {
    INSTANCE;
    
    private static RootAllocator rootAllocator = new RootAllocator(Long.MAX_VALUE);
    private static final AtomicInteger childNumber = new AtomicInteger(0);

    public static BufferAllocator getChildAllocator() {
        return rootAllocator.newChildAllocator(nextChildName(), 0, Long.MAX_VALUE);
    }

    private static String nextChildName() {
        return "Allocator-Child-" + childNumber.incrementAndGet();
    }

}