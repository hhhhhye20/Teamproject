			function popup_tfidf(frm) {
                                var url    ="/home/word_analysis";
                                var title  = "word_pop";
                                var status = "toolbar=no,directories=no,scrollbars=no,resizable=no,status=no,menubar=no,width=600, height=800, top=0,left=20";
                                window.open("", title,status);
                                frm.target = title;
                                frm.action = url;
                                frm.method = "post";
                                frm.submit();
                        }

                        function popup_cosine(frm) {
                                var url    ="/home/cosine_similarity";
                                var title  = "sim_pop";
                                var status = "toolbar=no,directories=no,scrollbars=no,resizable=no,status=no,menubar=no,width=600, height=400, top=0,left=20";
                                window.open("", title,status);
                                frm.target = title;
                                frm.action = url;
                                frm.method = "post";
                                frm.submit();
                        }

