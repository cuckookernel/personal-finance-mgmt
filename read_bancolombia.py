# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 19:35:46 2013

@author: Mateon
"""

import datetime as dt 

def high_level_key( rec ) : 
    typ= rec["type"]   
    if( rec["qty"] > 0 ) : 
        return "ingreso"
    elif( typ == "arriendo" or typ == "movistar" or typ == "une" ) : 
        return "arriendo + servicios"
    else : 
        return "gastos"

def read_txt( filename ) : 
    f = open( filename, "rb" )
    
    ret = {}

    count = 0; 
    
    for line in f.xreadlines() : 
        count += 1        
        if count == 1 : continue 
        cols = line.rstrip().split( "\t" )
        date_ps = cols[0].split( "/" )
        date_o = dt.date( int(date_ps[0]), int( date_ps[1]), int(date_ps[2]) )
        loc = cols[2]
        info = cols[3]
        qty  = float( cols[5].replace( ",", "" ) )
        
        typ = "?"
        typ2 = None 
        if( info.startswith('ABONO INTERESES') ) : 
            typ = "interes"            
            typ2 = "interes"
        elif( info.startswith( 'CUOTA MANEJO TARJETA DEBITO' )) :        
            typ = "interes"            
            typ2 = "cuota manejo"
            
        if( len( cols ) > 6 ) :
            typ = cols[6]
            
        rec = { "date" : date_o, 
                "month" : "%d/%d" % ( date_o.year,  date_o.month ),
                "loc" : loc ,
                "info"  : info,
                "qty" : qty, 
                "type" : typ, 
                "type2" : typ2,
                
                "cnt" : 1}
                
        rec["high_level"] = high_level_key( rec )
                
        if( typ != "_ignore" ) :
            ret[count] =  rec 
        elif( typ2 is None ) : 
            print("IGNORED: %s" % rec )

        # print( ret )         
        count += 1 
        # break             
    
    f.close()    
    return ret
    

    
def summary_key_1( recs, key1 ) : 
    summary = {} 
    
    for k,r in recs.iteritems()  :
        typ = r[key1]
        sum_rec = summary.get( typ, { "qty" : 0, "cnt" : 0 } ) 
        sum_rec["qty"] += r["qty"]
        sum_rec["cnt"] += r["cnt"]        
        summary[typ] = sum_rec                  
        
    return summary
  
    
def summary_key_2( recs, key1, key2 ) : 
    summary = { }     
    for key, rec in recs.iteritems() :        
        newkey = ( rec[key1], rec[key2] )
        sum_rec = summary.get( newkey, { "qty" : 0.0, "cnt" : 0 } )
        sum_rec["qty"] += rec["qty"]
        sum_rec["cnt"] += rec["cnt"]
        summary[newkey] = sum_rec         
    return summary 
   
  
def summary_month_type( recs  ) : 
    return summary_key_2( recs, "month", "type" )    
    
def display_summary_2keys( recs ) : 
    prev_key0 = None
    for key  in sorted( recs.keys() ) : 
        rec = recs[key]        
        key0 = key[0]
        key1 = key[1]
        if( key0 != prev_key0 ) : 
            print( "" )
        print( "%s\t%20s\t%9.0f\t%d" % ( key0, key1,
                                        rec["qty"], rec["cnt"]) )
        prev_key0 = key0
    print( "\n" )

def display_summary_1key( qty_map, factor = 1.0 ) :     
    for key, rec in qty_map.iteritems() :                 
        print( "%20s\t%9.0f" % ( key, rec['qty'] * factor ) )        

def display_unexplained( recs ) : 
    unexplained = [ r for r in recs.itervalues() if r["type"] == "?" ]
    recs_sorted = sorted( unexplained, key = lambda r : r["date"] )
    for r in recs_sorted : 
        print( "%s\t%9.0f\t%s\t%s" % ( r["date"], r["qty"], r["loc"], r["info"]) )
    
    
def group_by_high_level( recs ) :     
    high_level  = { }
    for r in recs : 
        month = r[ "month" ]
        key = ( month, high_level_key( r ) ) 
        high_level[key] = high_level.get( key, 0 ) + r["qty"]
    return high_level
    
def comp_and_disp_summary_month_type( filename ) : 
    recs =  read_txt( filename )
    all_dates = [r["date"] for r in recs.itervalues() ]
    max_date, min_date = max( all_dates ), min( all_dates )
    time_span = ( max_date - min_date ).days + 1.0 
    
    qty_type = summary_key_1( recs, key1 = "type" )
    print( "TOTALES: ")
    display_summary_1key( qty_type  )
    
    factor = 30.0 / time_span 
    print( "\nTOTALES / 30 dias: ")
    display_summary_1key( qty_type, factor = factor )
    
    print( "\n" )
    display_summary_2keys( summary_month_type( recs ) )
    
    high_level_sum = summary_key_2( recs, key1 = "month", 
                                       key2 = "high_level" )
    print( "High Level ")
    display_summary_2keys( high_level_sum )
    display_unexplained( recs )
    
