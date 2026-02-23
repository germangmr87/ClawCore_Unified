package ai.clawcore.android.ui

import androidx.compose.runtime.Composable
import ai.clawcore.android.MainViewModel
import ai.clawcore.android.ui.chat.ChatSheetContent

@Composable
fun ChatSheet(viewModel: MainViewModel) {
  ChatSheetContent(viewModel = viewModel)
}
