/*
 * This file is licensed under the Apache License 2.0. See the LICENSE file for details.
 */
package com.nirso.nirscanner.auth

import org.junit.Test
import org.junit.Assert.*

class AuthManagerTest {
    var authManager = AuthManager()

    @Test
    fun encryptedMessage_equalsString() {
        val originalMessage = "Hello World!"
        // Encrypt the message
        val encryptedMessage = authManager.encryptMessage(originalMessage)
        println(encryptedMessage)
        assertTrue(encryptedMessage != "")
    }


}