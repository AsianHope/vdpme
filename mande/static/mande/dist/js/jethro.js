/*!
 * Custom Jethro CSS
 */

//custom sorting for program titles
 $.fn.dataTable.ext.type.order['jethro-pre'] = function ( d ) {
      console.log(d);
     switch ( d ) {
         case 'Grade 1':     return 1;
         case 'Grade 2':     return 2;
         case 'Grade 3':     return 3;
         case 'Grade 4':     return 4;
         case 'Grade 5':     return 5;
         case 'Grade 6':     return 6;
         case 'Grade 7':     return 7;
         case 'Grade 8':     return 8;
         case 'Grade 9':     return 9;
         case 'Grade 10':    return 10;
         case 'Grade 11':    return 11;
         case 'Grade 12':    return 12;
         case 'English':     return 50;
         case 'Computers':  return 60;
         case 'Vietnamese':  return 70;
     }
     return 0;
 };
