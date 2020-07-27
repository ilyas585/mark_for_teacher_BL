function toggleCheckbox(element)
{
    debugger;
    if (element.checked) {
        $(".hiddenable-timetable-row").hide();
        $(".hiddenable-form").removeAttr('required');
        $(".hidden-input").val("First");


        var week_day_prefix = ["pn", "vt", "sr", "ct", "pt", "sb"];

        for (lesson_number = 1; lesson_number < 7; lesson_number++) {
            var input_name_origin1 = week_day_prefix[0] + "onest" + lesson_number;
            var value1 = document.getElementById(input_name_origin1).value;
            var input_name_origin2 = week_day_prefix[0] + "onefn" + lesson_number;
            var value2 = document.getElementById(input_name_origin2).value;

            var input_name_origin3 = week_day_prefix[0] + "twost" + lesson_number;
            var value3 = document.getElementById(input_name_origin3).value;

            var input_name_origin4 = week_day_prefix[0] + "twofn" + lesson_number;
            var value4 = document.getElementById(input_name_origin4).value;


            for (day = 1; day < 6; day++) {
                 var input_name1 = week_day_prefix[day] + "onest" + lesson_number
                 document.getElementById(input_name1).value = value1

                 var input_name2 = week_day_prefix[day] + "onefn" + lesson_number
                 document.getElementById(input_name2).value = value2

                 var input_name3 = week_day_prefix[day] + "twost" + lesson_number
                 document.getElementById(input_name3).value = value3

                 var input_name4 = week_day_prefix[day] + "twofn" + lesson_number
                 document.getElementById(input_name4).value = value4
            }
        }
   }
    else {
        $(".hiddenable-timetable-row").show();
        $(".hiddenable-form").prop('required', true)
        $(".hidden-input").val("Explicit");
    }
}
