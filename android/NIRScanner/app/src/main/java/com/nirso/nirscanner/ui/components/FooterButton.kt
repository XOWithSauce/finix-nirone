/*
 * This file is licensed under the Apache License 2.0. See the LICENSE file for details.
 */
package com.nirso.nirscanner.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ElevatedButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.nirso.nirscanner.ui.theme.inversePrimaryDark
import kotlinx.coroutines.launch

@Composable
fun FooterButton(text: String = "")  {
    val scope = rememberCoroutineScope()

    ElevatedButton(

        modifier = Modifier
            .padding(15.dp, 0.dp),
        onClick = {
            scope.launch {
                SnackbarManager.snackbarHostState.showSnackbar(
                    message = "You Pressed $text Button",
                    duration = SnackbarDuration.Short
                )
            }
        },
        enabled = true,
        border = BorderStroke(1.dp, color = MaterialTheme.colorScheme.scrim),
        contentPadding = PaddingValues(
            start = 30.dp,
            top = 10.dp,
            end = 30.dp,
            bottom = 10.dp
        ),
        elevation = ButtonDefaults.elevatedButtonElevation(
            defaultElevation = 5.dp,
            pressedElevation = 2.dp,
            focusedElevation = 5.dp,
            hoveredElevation = 5.dp,
            disabledElevation = 2.dp
        )
    ) {
        Text(
            color = MaterialTheme.colorScheme.inversePrimary,
            letterSpacing = 2.sp,
            fontSize = 16.sp,
            text = text
        )
    }
}