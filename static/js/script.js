document.oncontextmenu = function () {return false;}

// 参照画像を選択→表示
$('#input_ref').on('change', function (e) {
    var reader = new FileReader();
    reader.onload = function (e) {
        $("#img_ref").attr('src', e.target.result);
    }
    reader.readAsDataURL(e.target.files[0]);
});

// 対象画像を選択→表示
$('#input_sub').on('change', function (e) {
    var reader = new FileReader();
    reader.onload = function (e) {
        $("#img_sub").attr('src', e.target.result);
    }
    reader.readAsDataURL(e.target.files[0]);
});

$('.submit_btn').on("click", function(e){
    document.forms.submit_img.submit();
});

// ローディングアニメーション
function loadingAnimation(){
    $(".fa-circle-o-notch").show();
}

// Calcボタン制御
const isRef = document.getElementById("input_ref")
const isSub = document.getElementById("input_sub")
const btn = document.getElementById("calcImg")
function isFile(){
    if(isRef.files.length>0 && isSub.files.length>0)
        btn.classList.remove("disabled");
    else
        btn.classList.add("disabled");
}