/*jshint esversion: 6 */

/*
  Manage Information Link View With a current selected link
*/
var AskomicsLinksView = function () {
  var prefix = "rightview_";
  var arrowCode = "&#8594;";

  AskomicsLinksView.prototype.remove = function (link) {
    $("#"+prefix+"Link-"+link.source.id+"-"+link.target.id).remove();
  };

  AskomicsLinksView.prototype.showTitle = function (link) {

    nodeView.clean();
    $("#objectName").text(link.label);

  };

  AskomicsLinksView.prototype.show = function (link) {
    this.showTitle(link);
    $("#"+prefix+"Link-"+link.source.id+"-"+link.target.id).show();
  };

  AskomicsLinksView.prototype.hide = function (link) {
    $("#"+prefix+"Link-"+link.source.id+"-"+link.target.id).hide();
  };

  AskomicsLinksView.prototype.hideAll = function (link) {
    $("div[id*='"+ prefix +"']" ).hide();
  };

  AskomicsLinksView.prototype.changeDir = function(link, type) {
    link.type = type;
    //FIXME: following don't work (write the new label on link)
    var labels = {'included':'included in', 'excluded':'exluded of', 'overlap':'overlap with', 'near': 'near'};
    link.label = labels[type];
    console.log('link (alv): '+JSON.stringify(link));
    forceLayoutManager.update();
  };

  AskomicsLinksView.prototype.changeStrict = function(link, strict) {
    link.strict = strict;
  };

  AskomicsLinksView.prototype.changeSameTax = function(link, same_tax) {
    link.sameTax = same_tax;
  };

  AskomicsLinksView.prototype.changeSameRef = function(link, same_ref) {
    link.sameRef = same_ref;
  };

  AskomicsLinksView.prototype.create = function (link) {

    var id_link = link.source.id+"-"+link.target.id;

    var elemUri = link.uri,
         nameDiv = prefix+"Link-"+id_link ;

    this.showTitle(link);

    var details = $("<div></div>").attr("id",nameDiv).addClass('div-details');
    console.log(JSON.stringify(link.target));

    /*var reverseArrow = $('<div></div>').append($('<span><span>').attr('class', 'glyphicon glyphicon-resize-horizontal').attr('aria-hidden', 'true'))
                                       .append('Reverse direction');*/

    var select = $('<select></select>').attr('id', 'direction-'+id_link);

    var types = {'included': 'included in', 'excluded': 'excluded of', 'overlap': 'overlap with', 'near': 'near'};

    for (var key in types) {
      if(link.type == key) {
          select.append($('<option></option>').attr("value", key).attr("selected", "selected").append(types[key]));
      }else{
          select.append($('<option></option>').attr("value", key).append(types[key]));
      }
    }

    var relation = $("<div></div>").append(nodeView.formatLabelEntity(link.source))
                               .append(select)
                               .append(nodeView.formatLabelEntity(link.target));

    var checkbox_sameref;
    var checkbox_sametax;

    if (link.sameRef) {
      checkbox_sameref = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'ref-'+id_link).attr('checked', 'checked')).append('Reference');
    }else{
      checkbox_sameref = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'ref-'+id_link)).append('Reference');
    };

    if (link.sameTax) {
      checkbox_sametax = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'tax-'+id_link).attr('checked', 'checked')).append('Taxon');
    }else{
      checkbox_sametax = $('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'tax-'+id_link)).append('Taxon');
    };


    var onTheSame = $('<div></div>').append('On the same:')
                                    .append($('<br>'))
                                    .append(checkbox_sameref)
                                    .append($('<br>'))
                                    .append(checkbox_sametax);

    var strict;

    if (link.strict) {
      strict = $('<div></div>').append($('<label></label>').append($('<input>').attr('type', 'checkbox').attr('checked', 'checked').attr('id', 'strict-'+id_link).attr('value', 'strict')).append('Strict'));
    }else{
      strict = $('<div></div>').append($('<label></label>').append($('<input>').attr('type', 'checkbox').attr('id', 'strict-'+id_link).attr('value', 'strict')).append('Strict'));
    };

    details/*.append(reverseArrow)*/
           .append(relation)
           .append($('<hr>'))
           .append(onTheSame)
           .append($('<hr>'))
           .append(strict);

    alv = this;

    select.change(function() {
      value = select.val();
      alv.changeDir(link, value);
    });

    checkbox_sameref.change(function() {
      if ($('#ref-'+id_link).is(':checked')) {
        alv.changeSameRef(link, true);
      }else{
        alv.changeSameRef(link, false);
      }
    });

    checkbox_sametax.change(function() {
      if($('#tax-'+id_link).is(':checked')) {
        alv.changeSameTax(link, true);
      }else{
        alv.changeSameTax(link, false);
      }
    });

    strict.change(function() {
      if($('#strict-'+id_link).is(':checked')) {
        alv.changeStrict(link, true);
      }else{
        alv.changeStrict(link, false);
      }
    });

    $("#viewDetails").append(details);
  };

  // take a string and return an entity with a sub index
  AskomicsLinksView.prototype.selectListLinksUser = function(links,node) {
    /* fix the first link associted with the new instanciate node TODO: propose an interface to select the link */
  for (var il in links) {
    var l = links[il];
    console.log("===>"+JSON.stringify(l));
    if ( l.suggested && (l.source.id == node.id || l.target.id == node.id) ) {
        return [links[il]];
    }
  }

  //$('#linksModal').modal('hide');
    /*
    for (var l of links) {
        if ( l.suggested ) {
          if (l.source.id == d.id || l.target.id == d.id ) {
            graphBuilder.instanciateLink(l);
            graphView.solidifyLink(l);
            break ; //only the link finded....
          }
        }
    }*/
  };
};