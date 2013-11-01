package org.jaydebeapi.mockdriver;

import static org.hamcrest.CoreMatchers.notNullValue;
import static org.junit.Assert.assertThat;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

import org.junit.Test;

public class MockDriverTest {

	@Test
	public void test() throws Exception {
		Connection connection = DriverManager
				.getConnection("jdbc:jaydebeapi://dummyurl");
		assertThat(connection, notNullValue());
	}

	@Test(expected = SQLException.class)
	public void testWrongUrl() throws Exception {
		DriverManager.getConnection("jdbc:unkown://dummyurl", "user",
				"password");
	}

}
