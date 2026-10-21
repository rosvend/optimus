const dialog = document.querySelector<HTMLDialogElement>("#login")!;
const form = dialog.querySelector("form")!;
const input = dialog.querySelector<HTMLInputElement>("#api-key")!;
const error = dialog.querySelector<HTMLElement>("#login-error")!;

// The dashboard is useless without a key, so the dialog can't be dismissed with Escape
dialog.addEventListener("cancel", (event) => event.preventDefault());

export function askForApiKey(message = ""): Promise<string> {
  error.textContent = message;
  input.value = "";
  dialog.showModal();
  return new Promise((resolve) => {
    form.addEventListener(
      "submit",
      (event) => {
        event.preventDefault();
        dialog.close();
        resolve(input.value.trim());
      },
      { once: true },
    );
  });
}
