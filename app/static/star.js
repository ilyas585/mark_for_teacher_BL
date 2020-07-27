var count, r1, r2, r3;
document.getElementById("gl").classList.add('active');

function starmark(item)
{
    debugger;
    if (item.id[1] + item.id[2] + item.id[3] == "one")
    {
        r1 = item.id[0]
    }

    if (item.id[1] + item.id[2] + item.id[3] == "two")
    {
    r2 = item.id[0]
    }
    if (item.id[1] + item.id[2] + item.id[3] == "thr")
    {
    r3 = item.id[0]
    }
    count=item.id[0];
    sessionStorage.starRating = count;
    var subid= item.id.substring(1);
    for(var i=0;i<5;i++)
    {
    if(i<count)
    {
    document.getElementById((i+1)+subid).style.color="orange";
    }
    else
    {
    document.getElementById((i+1)+subid).style.color="black";
    }


    }

}

function result()
{
//Rating : Count
//Review : Comment(id)
if(r1 == undefined)
{
r1 = 1;
}
if(r2 == undefined)
{
r2 = 1;
}
if(r3 == undefined)
{
r3 = 1;
}

document.getElementById('ggg').value = r1;
document.getElementById('gg').value = r2;
document.getElementById('g').value = r3 +"//::spliter::"+document.getElementById('comment').value;

alert("Спасибо за отзыв");
}

