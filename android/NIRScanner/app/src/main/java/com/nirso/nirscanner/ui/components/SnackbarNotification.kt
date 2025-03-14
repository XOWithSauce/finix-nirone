/*
 * This file is licensed under the Apache License 2.0. See the LICENSE file for details.
 */
package com.nirso.nirscanner.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Snackbar
import androidx.compose.material3.SnackbarData
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable

object SnackbarManager {
    val snackbarHostState = SnackbarHostState()
}

@Composable
fun CustomSnackbar(snackbarData: SnackbarData) {
    Snackbar(
        action = {
            IconButton(onClick = { SnackbarManager.snackbarHostState.currentSnackbarData?.dismiss() }) {
                Icon(
                    imageVector = Icons.Rounded.Close,
                    contentDescription = "Close Snackbar",

                )
            }
        }
    ) {
        Text(snackbarData.visuals.message)
    }
}