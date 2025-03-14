/*
 * This file is licensed under the Apache License 2.0. See the LICENSE file for details.
 */
package com.nirso.nirscanner.auth

import android.os.Build
import androidx.annotation.RequiresApi
import androidx.compose.material3.SnackbarDuration
import com.nirso.nirscanner.BuildConfig
import com.nirso.nirscanner.ui.components.SnackbarManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.Mac
import javax.crypto.SecretKey
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString

class AuthManager {

    // Compose the classes
    private val authHmac: HmacAuth = HmacAuth(BuildConfig.SHARED_SIGN_KEY)
    private val authEncr: AesEncryption = AesEncryption(BuildConfig.SHARED_ENCR_KEY)

    @Serializable
    data class EncryptedMessage(
        var signature: String,
        var message: String,
        var iv: String
    )

    // Extension functions to ease serialization
    @RequiresApi(Build.VERSION_CODES.O)
    fun ByteArray.toBase64(): String =
        String(Base64.getEncoder().encode(this))

    @RequiresApi(Build.VERSION_CODES.O)
    fun String.toByteArrayFromBase64(): ByteArray =
        Base64.getDecoder().decode(this)

    @RequiresApi(Build.VERSION_CODES.O)
    fun encryptMessage(message: String): String {
        // Encrypt
        val iv = ByteArray(16)
        SecureRandom().nextBytes(iv)
        val encryptedMessage = authEncr.askToEncrypt(message, iv)
        val signature = authHmac.askForSignature(encryptedMessage)

        // Serialize to JSON
        val serMessage = encryptedMessage.toBase64()
        val serIv = iv.toBase64()
        val serializedData = mapOf(
            "signature" to signature,
            "message" to serMessage,
            "iv" to serIv
        )
        val result = Json.encodeToString(serializedData)
        return result
    }

    @RequiresApi(Build.VERSION_CODES.O)
    fun decryptMessage(jsonString: String, scope: CoroutineScope): String {
        var result = ""
        try {
            // Deserialize from JSON
            val encryptedMessage: EncryptedMessage = Json.decodeFromString<EncryptedMessage>(jsonString)

            val message = encryptedMessage.message.toByteArrayFromBase64()
            val iv = encryptedMessage.iv.toByteArrayFromBase64()

            // Auth and decrypt
            val genSign = authHmac.askForSignature(message)


            result = if (authHmac.compareDigest(encryptedMessage.signature, genSign)) {
                authEncr.askToDecrypt(message, iv, scope)
            } else {
                "SignNoMatch"
            }
        } catch (e: Exception) {
            result = "ErrorDecr ${e.message}"
        }
        return result
    }
}

class HmacAuth(shared_sign_key: String) {

    private val sharedKey = SecretKeySpec(shared_sign_key.toByteArray(), "HmacSHA256")

    @OptIn(ExperimentalStdlibApi::class)
    private fun genSignature(message: ByteArray): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(sharedKey)
        val result = mac.doFinal(message)
        return result.toHexString()
    }

    fun askForSignature(message: ByteArray): String {
        return genSignature(message)
    }

    fun compareDigest(recvSign: String, genSign: String): Boolean {
        return MessageDigest.isEqual(recvSign.toByteArray(), genSign.toByteArray())
    }
}


class AesEncryption(shared_encr_key: String) {

    private val sharedKey: SecretKey = SecretKeySpec(shared_encr_key.toByteArray(), "AES")

    private fun genCiphertext(message: ByteArray, iv: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        val ivSpec = IvParameterSpec(iv)
        cipher.init(Cipher.ENCRYPT_MODE, sharedKey, ivSpec)
        return cipher.doFinal(message)
    }

    private fun decMessage(ciphertext: ByteArray, iv: ByteArray, scope: CoroutineScope): ByteArray {
        var result: ByteArray = byteArrayOf()
        try {
            val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
            val ivSpec = IvParameterSpec(iv)
            cipher.init(Cipher.DECRYPT_MODE, sharedKey, ivSpec)
            result = cipher.doFinal(ciphertext).also {
                val padLength = it[it.size - 1].toInt()
                if (padLength in 1..16) {
                    result += it.copyOfRange(0, it.size - padLength)
                }
            }

        } catch (e: Exception) {
            scope.launch {
                SnackbarManager.snackbarHostState.showSnackbar(
                    message = "Decryption Error: ${e}",
                    duration = SnackbarDuration.Short
                )
            }
        }
        return result

    }

    fun askToEncrypt(message: String, iv: ByteArray): ByteArray {
        return genCiphertext(message.toByteArray(), iv)
    }

    fun askToDecrypt(message: ByteArray, iv: ByteArray, scope: CoroutineScope): String {
        val result = decMessage(message, iv, scope).decodeToString()
        return result
    }
}