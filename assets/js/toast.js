/*=====================
    toast js
   ==========================*/

const toastTrigger = document.getElementById("liveToastBtn");
const toastLiveExample = document.getElementById("liveToast");

if (toastTrigger) {
  const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample);
  toastTrigger.addEventListener("click", () => {
    toastBootstrap.show();
    navigator.clipboard.writeText(window.location.href).then(() => {
        console.log("success")
    })
  });
}
